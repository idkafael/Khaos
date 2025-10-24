import requests
import qrcode
import io
from config.config import Config
from typing import Dict, Optional
import json

class PaymentUtils:
    """Utilitários para processamento de pagamentos via Pix usando Multi-Gateway (Mercado Pago + PushinPay)"""
    
    def __init__(self):
        # Import do Gateway Selector (Mercado Pago + PushinPay)
        from utils.gateway_selector import GatewaySelector
        self.gateway_selector = GatewaySelector()
        
        # Debug: Verificar configuração
        print(f"💳 PaymentUtils: Usando Multi-Gateway (Mercado Pago prioritário)")
        gateways_disponiveis = self.gateway_selector.get_available_gateways()
        print(f"✅ Gateways disponíveis: {', '.join(gateways_disponiveis)}")
    
    async def create_pix_payment(self, amount: float, description: str, customer_email: str, customer_name: str, split_config: Optional[Dict] = None, guild_id: int = None, transaction_id: int = None) -> Optional[Dict]:
        """Cria um pagamento via Pix usando Multi-Gateway (Mercado Pago prioritário, PushinPay fallback)
        
        Args:
            amount: Valor do pagamento
            description: Descrição do pagamento
            customer_email: Email do cliente
            customer_name: Nome do cliente
            split_config: Configuração de split (opcional) - dict com 'recipient_id' e 'percent'
            guild_id: ID do servidor Discord (para identificar gateway preferido)
            transaction_id: ID da transação no banco
        """
        try:
            print(f"💳 Iniciando pagamento - Valor: R$ {amount:.2f}")
            print(f"📧 Cliente: {customer_name} ({customer_email})")
            print(f"📝 Descrição: {description}")
            
            # Validar valor mínimo (R$ 0,50)
            if amount < 0.50:
                print("❌ Valor mínimo é R$ 0,50")
                return None
            
            # Usar Gateway Selector para criar pagamento
            # Prioridade: Mercado Pago → PushinPay (fallback automático)
            payment_data = await self.gateway_selector.create_payment(
                guild_id=guild_id or 0,  # Se não tiver guild_id, usa 0 (vai usar Mercado Pago por padrão)
                amount=amount,
                description=description,
                transaction_id=transaction_id or 0,
                user_email=customer_email
            )
            
            if not payment_data:
                print("❌ Falha ao criar pagamento em TODOS os gateways")
                return None
            
            # Identificar qual gateway foi usado
            gateway_used = payment_data.get('gateway_used', 'mercadopago')
            print(f"✅ Pagamento criado via {gateway_used.upper()}")
            
            # Normalizar resposta para formato esperado
            if gateway_used == 'mercadopago':
                # Mercado Pago retorna: qr_code_base64, qr_code (pix copia e cola), payment_id
                qr_code_data = payment_data.get('qr_code', '')
                payment_id = payment_data.get('payment_id', '')
                
                print(f"✅ [PaymentUtils] Mercado Pago payment created: ID {payment_id}")
                
                # Gerar QR Code visual
                qr_code_image = self._generate_qr_code(qr_code_data) if qr_code_data else None
                
                return {
                    'id': payment_id,
                    'pix_code': qr_code_data,
                    'qr_code': qr_code_data,
                    'qr_code_image': qr_code_image,
                    'qr_code_base64': payment_data.get('qr_code_base64', ''),
                    'status': payment_data.get('status', 'pending'),
                    'value': amount,
                    'correlation_id': f"discord_{customer_name}_{int(amount*100)}",
                    'gateway_used': 'mercadopago'
                }
            
            elif gateway_used == 'pushinpay':
                # PushinPay retorna estrutura diferente
                qr_code_data = payment_data.get('qr_code', '')
                payment_id = payment_data.get('id', '')
                
                # Gerar QR Code visual
                qr_code_image = self._generate_qr_code(qr_code_data) if qr_code_data else None
                
                return {
                    'id': payment_id,
                    'pix_code': qr_code_data,
                    'qr_code': qr_code_data,
                    'qr_code_image': qr_code_image,
                    'qr_code_base64': payment_data.get('qr_code_base64', ''),
                    'status': payment_data.get('status', 'created'),
                    'value': amount,
                    'value_cents': int(amount * 100),
                    'correlation_id': f"discord_{customer_name}_{int(amount*100)}",
                    'gateway_used': 'pushinpay'
                }
            
            else:
                print(f"⚠️ Gateway desconhecido: {gateway_used}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar pagamento Pix: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def check_payment_status(self, transaction_id: str) -> str:
        """Verifica o status de um pagamento"""
        try:
            # Buscar transação no banco de dados primeiro
            from models.transaction_model import TransactionModel
            transaction_model = TransactionModel()
            transaction = await transaction_model.get_transaction(int(transaction_id))
            
            if not transaction or not transaction.get('payment_id'):
                return 'pending'
            
            payment_id = transaction['payment_id']
            
            # Verificar status na API PushinPay
            response = requests.get(
                f"{self.base_url}/api/transactions/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                payment_info = response.json()
                status = payment_info.get('status', 'created')
                
                # Mapear status da PushinPay para nosso sistema
                status_mapping = {
                    'created': 'pending',
                    'paid': 'approved',
                    'expired': 'failed'
                }
                
                return status_mapping.get(status, 'pending')
            elif response.status_code == 404:
                print("Transação não encontrada na PushinPay")
                return 'failed'
            else:
                print(f"Erro ao verificar status: {response.status_code} - {response.text}")
                return 'pending'
                
        except Exception as e:
            print(f"Erro ao verificar status do pagamento: {e}")
            return 'pending'
    
    def _generate_qr_code(self, data: str) -> Optional[io.BytesIO]:
        """Gera um QR Code a partir dos dados fornecidos"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para BytesIO
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"Erro ao gerar QR Code: {e}")
            return None
    
    async def cancel_payment(self, payment_id: str) -> bool:
        """Cancela um pagamento (PushinPay não tem endpoint de cancelamento)"""
        try:
            # PushinPay não oferece cancelamento via API
            # O pagamento expira automaticamente após um tempo
            print("⚠️ PushinPay não oferece cancelamento via API. O pagamento expirará automaticamente.")
            return False
            
        except Exception as e:
            print(f"Erro ao cancelar pagamento: {e}")
            return False
    
    async def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """Obtém detalhes de um pagamento"""
        try:
            response = requests.get(
                f"{self.base_url}/api/transactions/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"Erro ao obter detalhes: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao obter detalhes do pagamento: {e}")
            return None
    
    def format_pix_code(self, pix_code: str) -> str:
        """Formata o código Pix para exibição"""
        if not pix_code:
            return "Código não disponível"
        
        # Adicionar quebras de linha a cada 77 caracteres (padrão Pix)
        formatted = ""
        for i in range(0, len(pix_code), 77):
            formatted += pix_code[i:i+77] + "\n"
        
        return formatted.strip()
    
    def validate_email(self, email: str) -> bool:
        """Valida se o email está em formato válido"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def format_currency(self, amount: float) -> str:
        """Formata valor monetário para exibição"""
        return f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def get_qr_code_image_from_base64(self, qr_code_base64: str) -> Optional[io.BytesIO]:
        """Converte QR Code base64 da PushinPay para BytesIO"""
        try:
            if not qr_code_base64:
                return None
            
            # Remover prefixo data:image/png;base64, se existir
            if qr_code_base64.startswith('data:image'):
                qr_code_base64 = qr_code_base64.split(',')[1]
            
            import base64
            image_data = base64.b64decode(qr_code_base64)
            
            # Converter para BytesIO
            image_buffer = io.BytesIO(image_data)
            image_buffer.seek(0)
            
            return image_buffer
            
        except Exception as e:
            print(f"Erro ao converter QR Code base64: {e}")
            return None
