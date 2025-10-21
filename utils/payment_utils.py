import requests
import qrcode
import io
from config.config import Config
from typing import Dict, Optional
import json

class PaymentUtils:
    """Utilitários para processamento de pagamentos via Pix usando PushinPay"""
    
    def __init__(self):
        self.pushinpay_api_key = Config.PUSHINPAY_API_KEY
        self.pushinpay_base_url = "https://api.pushinpay.com.br"
        self.pushinpay_sandbox_url = "https://api-sandbox.pushinpay.com.br"
        self.use_sandbox = False  # FORÇAR PRODUÇÃO
        self.base_url = self.pushinpay_base_url  # SEMPRE PRODUÇÃO
        self.headers = {
            "Authorization": f"Bearer {self.pushinpay_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Debug: Verificar configuração
        print(f"🚀 PRODUÇÃO PaymentUtils: API Key carregada: {self.pushinpay_api_key[:10]}...")
        print(f"🚀 PRODUÇÃO PaymentUtils: Modo: PRODUÇÃO (não sandbox)")
        print(f"🚀 PRODUÇÃO PaymentUtils: Base URL: {self.base_url}")
        print(f"🚀 PRODUÇÃO PaymentUtils: Headers: {self.headers}")
    
    async def create_pix_payment(self, amount: float, description: str, customer_email: str, customer_name: str, split_config: Optional[Dict] = None) -> Optional[Dict]:
        """Cria um pagamento via Pix usando a API PushinPay
        
        Args:
            amount: Valor do pagamento
            description: Descrição do pagamento
            customer_email: Email do cliente
            customer_name: Nome do cliente
            split_config: Configuração de split (opcional) - dict com 'recipient_id' e 'percent'
        """
        try:
            print(f"🔧 Debug: Iniciando pagamento - Valor: {amount}, Email: {customer_email}")
            print(f"🔧 Debug: API Key: {self.pushinpay_api_key[:10]}...")
            print(f"🔧 Debug: Base URL: {self.base_url}")
            
            # Converter valor para centavos (PushinPay usa centavos)
            amount_cents = int(amount * 100)
            
            # Validar valor mínimo (50 centavos)
            if amount_cents < 50:
                print("❌ Valor mínimo é R$ 0,50 (50 centavos)")
                return None
            
            # Preparar regras de split se configurado
            split_rules = []
            if split_config and split_config.get('recipient_id') and split_config.get('percent'):
                recipient_id = split_config['recipient_id']
                split_percent = float(split_config['percent'])
                split_amount = int(amount_cents * (split_percent / 100))
                
                split_rules.append({
                    "recipient_id": recipient_id,
                    "amount": split_amount,
                    "liable": True,  # Responsável por chargebacks
                    "charge_processing_fee": False
                })
                
                print(f"🔧 Debug: Split configurado - Destinatário: {recipient_id}, Percentual: {split_percent}%, Valor: {split_amount} centavos")
            
            # Dados do pagamento para PushinPay
            payment_data = {
                "value": amount_cents,
                "split_rules": split_rules
            }
            
            print(f"🔧 Debug: Dados do pagamento: {payment_data}")
            print(f"🔧 Debug: Headers: {self.headers}")
            
            # Fazer requisição para a API PushinPay
            url = f"{self.base_url}/api/pix/cashIn"
            print(f"🔧 Debug: URL da requisição: {url}")
            print(f"🔧 Debug: Método: POST")
            print(f"🔧 Debug: JSON data: {payment_data}")
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payment_data,
                timeout=30
            )
            
            print(f"🔧 Debug: Status da resposta: {response.status_code}")
            print(f"🔧 Debug: Resposta: {response.text}")
            
            if response.status_code == 200:
                payment_info = response.json()
                
                # Extrair dados do QR Code
                qr_code_data = payment_info.get('qr_code', '')
                qr_code_id = payment_info.get('id', '')
                qr_code_base64 = payment_info.get('qr_code_base64', '')
                
                # Gerar QR Code visual
                qr_code_image = self._generate_qr_code(qr_code_data)
                
                return {
                    'id': qr_code_id,
                    'pix_code': qr_code_data,
                    'qr_code': qr_code_data,
                    'qr_code_image': qr_code_image,
                    'qr_code_base64': qr_code_base64,
                    'status': payment_info.get('status', 'created'),
                    'value': amount,
                    'value_cents': amount_cents,
                    'correlation_id': f"discord_{customer_name}_{amount_cents}",
                    'webhook_url': payment_info.get('webhook_url'),
                    'end_to_end_id': payment_info.get('end_to_end_id'),
                    'payer_name': payment_info.get('payer_name'),
                    'payer_national_registration': payment_info.get('payer_national_registration')
                }
            else:
                print(f"Erro na API PushinPay: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao criar pagamento Pix: {e}")
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
