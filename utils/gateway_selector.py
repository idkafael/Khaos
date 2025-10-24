"""
Seletor de Gateway de Pagamento
Suporta múltiplos gateways (Mercado Pago, PushinPay) com fallback automático
"""

from typing import Optional, Dict
from utils.mercadopago_manager import MercadoPagoManager
from models.guild_config_model import GuildConfigModel
import os
import requests

class GatewaySelector:
    """Seleciona gateway apropriado e realiza fallback se necessário"""
    
    def __init__(self):
        self.mp_manager = MercadoPagoManager()
        self.guild_config_model = GuildConfigModel()
        
        # Ordem de preferência padrão
        self.default_priority = ['mercadopago', 'pushinpay']
    
    async def get_preferred_gateway(self, guild_id: int) -> str:
        """
        Retorna gateway preferido do servidor
        
        Args:
            guild_id: ID do servidor
            
        Returns:
            Nome do gateway ('mercadopago', 'pushinpay', etc)
        """
        try:
            config = await self.guild_config_model.get_config(guild_id)
            
            if config and config.get('preferred_gateway'):
                return config['preferred_gateway']
            
            # Padrão: Mercado Pago
            return 'mercadopago'
            
        except Exception as e:
            print(f"❌ Erro ao buscar gateway preferido: {e}")
            return 'mercadopago'
    
    async def set_preferred_gateway(self, guild_id: int, gateway: str) -> bool:
        """
        Define gateway preferido do servidor
        
        Args:
            guild_id: ID do servidor
            gateway: Nome do gateway
            
        Returns:
            True se salvo com sucesso
        """
        try:
            valid_gateways = ['mercadopago', 'pushinpay', 'asaas', 'stripe']
            
            if gateway not in valid_gateways:
                print(f"❌ Gateway inválido: {gateway}")
                return False
            
            await self.guild_config_model.create_or_update_config(
                guild_id=guild_id,
                preferred_gateway=gateway
            )
            
            print(f"✅ Gateway preferido definido: {gateway}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar gateway: {e}")
            return False
    
    def is_gateway_available(self, gateway: str) -> bool:
        """
        Verifica se gateway está configurado e disponível
        
        Args:
            gateway: Nome do gateway
            
        Returns:
            True se disponível
        """
        if gateway == 'mercadopago':
            return self.mp_manager.is_configured()
        
        elif gateway == 'pushinpay':
            # PushinPay temporariamente desabilitado (focus em Mercado Pago)
            return False
        
        # Outros gateways
        return False
    
    async def create_payment(
        self,
        guild_id: int,
        amount: float,
        description: str,
        transaction_id: int,
        user_email: str = None,
        preferred_gateway: str = None
    ) -> Optional[Dict]:
        """
        Cria pagamento usando gateway preferido com fallback automático
        
        Args:
            guild_id: ID do servidor
            amount: Valor do pagamento
            description: Descrição
            transaction_id: ID da transação
            user_email: Email do usuário (opcional)
            preferred_gateway: Forçar gateway específico (opcional)
            
        Returns:
            Dict com dados do pagamento + 'gateway_used'
        """
        try:
            # Determinar gateway a usar
            if not preferred_gateway:
                preferred_gateway = await self.get_preferred_gateway(guild_id)
            
            # Tentar gateway preferido primeiro
            payment = await self._try_payment(
                gateway=preferred_gateway,
                amount=amount,
                description=description,
                transaction_id=transaction_id,
                user_email=user_email
            )
            
            if payment:
                payment['gateway_used'] = preferred_gateway
                print(f"✅ Pagamento criado via {preferred_gateway}")
                return payment
            
            # Fallback: tentar outros gateways
            print(f"⚠️ Falha no {preferred_gateway}, tentando fallback...")
            
            for gateway in self.default_priority:
                if gateway == preferred_gateway:
                    continue  # Já tentamos
                
                if not self.is_gateway_available(gateway):
                    continue
                
                payment = await self._try_payment(
                    gateway=gateway,
                    amount=amount,
                    description=description,
                    transaction_id=transaction_id,
                    user_email=user_email
                )
                
                if payment:
                    payment['gateway_used'] = gateway
                    print(f"✅ Pagamento criado via {gateway} (fallback)")
                    return payment
            
            # Nenhum gateway funcionou
            print("❌ Todos os gateways falharam")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao criar pagamento: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _try_payment(
        self,
        gateway: str,
        amount: float,
        description: str,
        transaction_id: int,
        user_email: str = None
    ) -> Optional[Dict]:
        """
        Tenta criar pagamento em gateway específico
        
        Returns:
            Dict com dados do pagamento ou None se falhar
        """
        try:
            if gateway == 'mercadopago':
                # Buscar informações do produto se houver transaction_id
                item_title = None
                item_category = None
                item_id = None
                
                if transaction_id:
                    try:
                        from models.transaction_model import TransactionModel
                        from models.product_model import ProductModel
                        
                        transaction_model = TransactionModel()
                        product_model = ProductModel()
                        
                        # Buscar transação para pegar product_id
                        transaction = await transaction_model.get_transaction(transaction_id)
                        if transaction and transaction.get('product_id'):
                            product = await product_model.get_product_by_id(transaction['product_id'])
                            if product:
                                item_title = product.get('name')
                                item_category = product.get('category', 'digital_goods')
                                item_id = product.get('id')
                                print(f"📦 [GatewaySelector] Produto encontrado: {item_title}")
                    except Exception as e:
                        print(f"⚠️ [GatewaySelector] Erro ao buscar produto: {e}")
                
                # Extrair nome/sobrenome do email se possível
                payer_first_name = None
                payer_last_name = None
                if user_email:
                    email_parts = user_email.split('@')[0].replace('.', ' ').replace('_', ' ')
                    name_parts = email_parts.split()
                    if len(name_parts) >= 1:
                        payer_first_name = name_parts[0].capitalize()
                    if len(name_parts) >= 2:
                        payer_last_name = ' '.join(name_parts[1:]).capitalize()
                
                return await self.mp_manager.create_pix_payment(
                    amount=amount,
                    description=description,
                    transaction_id=transaction_id,
                    payer_email=user_email,
                    payer_first_name=payer_first_name,
                    payer_last_name=payer_last_name,
                    item_title=item_title,
                    item_category=item_category,
                    item_id=str(item_id) if item_id else None,
                    item_quantity=1
                )
            
            elif gateway == 'pushinpay':
                # PushinPay temporariamente desabilitado para evitar importação circular
                # Mercado Pago é o gateway principal agora
                print(f"⚠️ PushinPay fallback desabilitado - Use Mercado Pago")
                return None
            
            else:
                print(f"❌ Gateway não implementado: {gateway}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar pagamento no {gateway}: {e}")
            return None
    
    def get_available_gateways(self) -> list:
        """
        Retorna lista de gateways disponíveis (configurados)
        
        Returns:
            Lista de nomes dos gateways
        """
        available = []
        
        if self.is_gateway_available('mercadopago'):
            available.append('mercadopago')
        
        if self.is_gateway_available('pushinpay'):
            available.append('pushinpay')
        
        return available
    
    def get_gateway_info(self, gateway: str) -> Dict:
        """
        Retorna informações sobre um gateway
        
        Args:
            gateway: Nome do gateway
            
        Returns:
            Dict com info do gateway
        """
        gateway_info = {
            'mercadopago': {
                'name': 'Mercado Pago',
                'icon': '💳',
                'description': 'Gateway principal - Pix instantâneo',
                'features': ['Pix', 'Cartão', 'Boleto'],
                'configured': self.is_gateway_available('mercadopago')
            },
            'pushinpay': {
                'name': 'PushinPay',
                'icon': '🔵',
                'description': 'Gateway alternativo - Pix rápido',
                'features': ['Pix'],
                'configured': self.is_gateway_available('pushinpay')
            },
            'asaas': {
                'name': 'Asaas',
                'icon': '🟢',
                'description': 'Em breve',
                'features': ['Pix', 'Boleto', 'Cartão'],
                'configured': False
            },
            'stripe': {
                'name': 'Stripe',
                'icon': '🟣',
                'description': 'Pagamentos internacionais',
                'features': ['Cartão Internacional', 'PayPal'],
                'configured': False
            }
        }
        
        return gateway_info.get(gateway, {
            'name': gateway,
            'icon': '❓',
            'description': 'Gateway desconhecido',
            'features': [],
            'configured': False
        })

