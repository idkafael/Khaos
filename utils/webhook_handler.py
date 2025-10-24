from aiohttp import web
import asyncio
import json
from typing import Optional
from utils.delivery_manager import DeliveryManager
from models.transaction_model import TransactionModel

class WebhookHandler:
    """Servidor webhook para receber notificações da PushinPay"""
    
    def __init__(self, bot, port: int = 8080):
        self.bot = bot
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.delivery_manager = DeliveryManager(bot)
        self.transaction_model = TransactionModel()
        
        # Configurar rotas
        self.app.router.add_post('/webhook/pushinpay', self.handle_pushinpay_webhook)
        self.app.router.add_post('/webhook/mercadopago', self.handle_mercadopago_webhook)
        self.app.router.add_get('/health', self.health_check)
    
    async def start(self):
        """Inicia o servidor webhook"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            print(f"🌐 Webhook server iniciado na porta {self.port}")
            print(f"📍 Endpoint: http://0.0.0.0:{self.port}/webhook/pushinpay")
        except Exception as e:
            print(f"❌ Erro ao iniciar webhook server: {e}")
            import traceback
            traceback.print_exc()
    
    async def stop(self):
        """Para o servidor webhook"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            print("🛑 Webhook server parado")
        except Exception as e:
            print(f"❌ Erro ao parar webhook server: {e}")
    
    async def health_check(self, request):
        """Endpoint de health check"""
        return web.json_response({'status': 'ok', 'service': 'webhook_handler'})
    
    async def handle_pushinpay_webhook(self, request):
        """Processa webhooks da PushinPay"""
        try:
            # Ler dados do webhook
            data = await request.json()
            
            print(f"📨 Webhook recebido: {json.dumps(data, indent=2)}")
            
            # Extrair informações do webhook
            payment_id = data.get('id')
            status = data.get('status')
            
            if not payment_id:
                print("⚠️ Webhook sem payment_id")
                return web.json_response({'error': 'payment_id missing'}, status=400)
            
            # Buscar transação pelo payment_id
            transaction = await self._find_transaction_by_payment_id(payment_id)
            
            if not transaction:
                print(f"⚠️ Transação não encontrada para payment_id: {payment_id}")
                return web.json_response({'error': 'transaction not found'}, status=404)
            
            print(f"📦 Webhook para transação #{transaction['id']} - Status: {status}")
            
            # Processar baseado no status
            if status == 'paid':
                # Pagamento confirmado - entregar produto
                asyncio.create_task(
                    self.delivery_manager.process_payment_confirmation(
                        transaction['id'],
                        payment_id
                    )
                )
                print(f"✅ Processando entrega para transação #{transaction['id']}")
                
            elif status == 'expired' or status == 'failed':
                # Pagamento expirado ou falhou
                await self.transaction_model.update_transaction(
                    transaction['id'],
                    {'status': 'expired'}
                )
                print(f"⏰ Transação #{transaction['id']} marcada como expirada")
                
                # Liberar estoque se reservado
                await self._release_reserved_stock(transaction['id'])
            
            # Retornar sucesso
            return web.json_response({
                'status': 'ok',
                'transaction_id': transaction['id'],
                'processed': True
            })
            
        except json.JSONDecodeError:
            print("❌ Webhook com JSON inválido")
            return web.json_response({'error': 'invalid json'}, status=400)
        except Exception as e:
            print(f"❌ Erro ao processar webhook: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_mercadopago_webhook(self, request):
        """Processa webhooks do Mercado Pago"""
        try:
            # Mercado Pago envia dados via query params e body
            query_params = request.rel_url.query
            
            # Tipo de notificação
            topic = query_params.get('topic') or query_params.get('type')
            resource_id = query_params.get('id')
            
            print(f"📨 Webhook Mercado Pago - Topic: {topic}, ID: {resource_id}")
            
            # Mercado Pago pode enviar vários tipos de notificação
            # Nos interessa apenas 'payment' e 'merchant_order'
            if topic not in ['payment', 'merchant_order']:
                print(f"⚠️ Tipo de webhook ignorado: {topic}")
                return web.json_response({'status': 'ignored'})
            
            # Buscar informações do pagamento via API
            from utils.mercadopago_manager import MercadoPagoManager
            mp_manager = MercadoPagoManager()
            
            if topic == 'payment':
                payment_info = await mp_manager.check_payment_status(resource_id)
                
                if not payment_info:
                    print(f"❌ Não foi possível buscar informações do pagamento {resource_id}")
                    return web.json_response({'error': 'payment not found'}, status=404)
                
                # Buscar transação pelo external_reference (nosso transaction_id)
                external_ref = payment_info.get('external_reference')
                
                if not external_ref:
                    print("⚠️ Webhook sem external_reference")
                    return web.json_response({'error': 'external_reference missing'}, status=400)
                
                # Buscar transação
                try:
                    transaction_id = int(external_ref)
                    transaction = await self.transaction_model.get_transaction_by_id(transaction_id)
                except:
                    print(f"❌ Transaction ID inválido: {external_ref}")
                    return web.json_response({'error': 'invalid transaction_id'}, status=400)
                
                if not transaction:
                    print(f"⚠️ Transação não encontrada: {transaction_id}")
                    return web.json_response({'error': 'transaction not found'}, status=404)
                
                print(f"📦 Webhook para transação #{transaction['id']} - Status: {payment_info['status']}")
                
                # Processar baseado no status
                if payment_info['status'] == 'approved':
                    # Pagamento aprovado - creditar carteira + entregar produto
                    
                    # 1. Creditar carteira do servidor
                    from models.wallet_model import WalletModel
                    from decimal import Decimal
                    
                    wallet_model = WalletModel()
                    
                    amount = Decimal(str(transaction['amount']))
                    guild_id = transaction['guild_id']
                    
                    await wallet_model.credit_wallet(
                        guild_id=guild_id,
                        amount=amount,
                        transaction_id=transaction['id'],
                        description=f"Venda via Mercado Pago - Pagamento {resource_id}"
                    )
                    
                    # 2. Entregar produto ao cliente
                    asyncio.create_task(
                        self.delivery_manager.process_payment_confirmation(
                            transaction['id'],
                            resource_id
                        )
                    )
                    
                    print(f"✅ Carteira creditada + Entrega processando para transação #{transaction['id']}")
                    
                elif payment_info['status'] in ['rejected', 'cancelled', 'refunded']:
                    # Pagamento rejeitado/cancelado
                    await self.transaction_model.update_transaction(
                        transaction['id'],
                        {'status': 'failed'}
                    )
                    print(f"❌ Transação #{transaction['id']} marcada como falhada")
                    
                    # Liberar estoque se reservado
                    await self._release_reserved_stock(transaction['id'])
                
                # Retornar sucesso
                return web.json_response({
                    'status': 'ok',
                    'transaction_id': transaction['id'],
                    'payment_status': payment_info['status'],
                    'processed': True
                })
            
            # Outros tipos de webhook
            return web.json_response({'status': 'ok'})
            
        except Exception as e:
            print(f"❌ Erro ao processar webhook Mercado Pago: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({'error': str(e)}, status=500)
    
    async def _find_transaction_by_payment_id(self, payment_id: str) -> Optional[dict]:
        """Busca transação pelo payment_id"""
        try:
            # A TransactionModel não tem método para buscar por payment_id
            # Vamos usar o Supabase diretamente
            from supabase import create_client
            from config.config import Config
            
            supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            result = supabase.table('transactions').select('*').eq('payment_id', payment_id).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Erro ao buscar transação por payment_id: {e}")
            return None
    
    async def _release_reserved_stock(self, transaction_id: int):
        """Libera estoque reservado para uma transação expirada"""
        try:
            from models.inventory_model import InventoryModel
            inventory_model = InventoryModel()
            
            inventory_item = await inventory_model.get_inventory_by_transaction(transaction_id)
            if inventory_item and inventory_item.get('status') == 'reserved':
                await inventory_model.release_reservation(inventory_item['id'])
                print(f"🔓 Estoque liberado para transação #{transaction_id}")
        except Exception as e:
            print(f"❌ Erro ao liberar estoque: {e}")

