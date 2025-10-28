import asyncio
from datetime import datetime, timedelta
from models.transaction_model import TransactionModel
from utils.payment_utils import PaymentUtils
from utils.delivery_manager import DeliveryManager
from typing import Optional

class PaymentChecker:
    """Sistema de polling para verificar status de pagamentos"""
    
    def __init__(self, bot):
        self.bot = bot
        self.transaction_model = TransactionModel()
        self.payment_utils = PaymentUtils()
        self.delivery_manager = DeliveryManager(bot)
        self.is_running = False
    
    async def start_checking(self):
        """Inicia o loop de verificação de pagamentos"""
        if self.is_running:
            print("⚠️ Payment checker já está rodando")
            return
        
        self.is_running = True
        print("🔄 Payment checker iniciado - Verificando a cada 10 segundos")
        
        while self.is_running:
            try:
                await self._check_pending_payments()
                await asyncio.sleep(10)  # 10 segundos
            except Exception as e:
                print(f"❌ Erro no payment checker: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(10)
    
    def stop_checking(self):
        """Para o loop de verificação"""
        self.is_running = False
        print("🛑 Payment checker parado")
    
    async def _check_pending_payments(self):
        """Verifica todos os pagamentos pendentes"""
        try:
            # Buscar transações pendentes criadas há menos de 30 minutos
            pending_transactions = await self.transaction_model.get_transactions_by_status('pending')
            
            if not pending_transactions:
                return
            
            now = datetime.now()
            checked = 0
            confirmed = 0
            expired = 0
            
            for transaction in pending_transactions:
                # Verificar idade da transação
                created_at = datetime.fromisoformat(transaction['created_at'].replace('Z', '+00:00'))
                age_minutes = (now - created_at.replace(tzinfo=None)).total_seconds() / 60
                
                # Expirar transações com mais de 30 minutos
                if age_minutes > 30:
                    await self._expire_transaction(transaction)
                    expired += 1
                    continue
                
                # Verificar status na API
                payment_status = await self._check_payment_status(transaction)
                
                # Mercado Pago usa 'approved' para pagamento confirmado
                if payment_status == 'approved' or payment_status == 'paid':
                    # Processar entrega
                    success = await self.delivery_manager.process_payment_confirmation(
                        transaction['id'],
                        transaction.get('payment_id')
                    )
                    if success:
                        confirmed += 1
                elif payment_status == 'expired' or payment_status == 'failed' or payment_status == 'rejected':
                    await self._expire_transaction(transaction)
                    expired += 1
                
                checked += 1
                
                # Pequeno delay para não sobrecarregar a API
                await asyncio.sleep(1)
            
            if checked > 0:
                print(f"🔍 Verificados: {checked} pagamentos | ✅ Confirmados: {confirmed} | ⏰ Expirados: {expired}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar pagamentos pendentes: {e}")
            import traceback
            traceback.print_exc()
    
    async def _check_payment_status(self, transaction: dict) -> Optional[str]:
        """Verifica o status de um pagamento específico na API Mercado Pago"""
        try:
            payment_id = transaction.get('payment_id')
            if not payment_id:
                print(f"⚠️ Transação #{transaction['id']} sem payment_id")
                return None
            
            # Usar Gateway Selector para verificar status (Mercado Pago)
            from utils.gateway_selector import GatewaySelector
            gateway_selector = GatewaySelector()
            
            # Verificar no Mercado Pago
            from utils.mercadopago_manager import MercadoPagoManager
            mp_manager = MercadoPagoManager()
            
            payment_info = await mp_manager.check_payment_status(payment_id)
            
            if payment_info:
                status = payment_info.get('status')
                print(f"📊 Transação #{transaction['id']} - Status Mercado Pago: {status}")
                return status
            else:
                print(f"⚠️ Pagamento {payment_id} não encontrado no Mercado Pago")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao verificar status do pagamento: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _expire_transaction(self, transaction: dict):
        """Marca uma transação como expirada"""
        try:
            # Atualizar status
            await self.transaction_model.update_transaction(
                transaction['id'],
                {'status': 'expired'}
            )
            
            # Liberar estoque reservado se existir
            from models.inventory_model import InventoryModel
            inventory_model = InventoryModel()
            
            inventory_item = await inventory_model.get_inventory_by_transaction(transaction['id'])
            if inventory_item and inventory_item.get('status') == 'reserved':
                await inventory_model.release_reservation(inventory_item['id'])
                print(f"🔓 Estoque liberado para transação #{transaction['id']}")
            
            # Notificar usuário se o canal ainda existir
            channel_id = transaction.get('delivery_channel_id')
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    import discord
                    embed = discord.Embed(
                        title="⏰ Pagamento Expirado",
                        description="O tempo para pagamento expirou (30 minutos).",
                        color=0xff0000
                    )
                    embed.add_field(
                        name="💡 Quer comprar novamente?",
                        value="Clique no botão de criar ticket novamente para gerar um novo pagamento.",
                        inline=False
                    )
                    await channel.send(embed=embed)
            
            print(f"⏰ Transação #{transaction['id']} marcada como expirada")
            
        except Exception as e:
            print(f"❌ Erro ao expirar transação: {e}")

