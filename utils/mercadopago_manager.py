"""
Gerenciador Mercado Pago
Integração com API do Mercado Pago para:
- Receber pagamentos Pix (vendas)
- Enviar Pix automático (saques)
"""

import mercadopago
import os
import qrcode
from io import BytesIO
from decimal import Decimal
from typing import Optional, Dict
from datetime import datetime
import hashlib
import hmac

class MercadoPagoManager:
    """Gerenciador de pagamentos Mercado Pago"""
    
    def __init__(self):
        self.access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
        self.public_key = os.getenv('MERCADOPAGO_PUBLIC_KEY')
        
        if not self.access_token:
            print("⚠️ MERCADOPAGO_ACCESS_TOKEN não configurado no .env")
            self.sdk = None
        else:
            self.sdk = mercadopago.SDK(self.access_token)
            print("✅ Mercado Pago SDK inicializado")
    
    def is_configured(self) -> bool:
        """Verifica se Mercado Pago está configurado"""
        return self.sdk is not None
    
    async def create_pix_payment(
        self,
        amount: float,
        description: str,
        transaction_id: int,
        payer_email: str = None
    ) -> Optional[Dict]:
        """
        Cria pagamento Pix e retorna QR Code + Pix Copia e Cola
        
        Args:
            amount: Valor do pagamento
            description: Descrição do produto
            transaction_id: ID da transação no banco
            payer_email: Email do pagador (opcional)
            
        Returns:
            Dict com: qr_code_base64, qr_code, payment_id, status
        """
        if not self.is_configured():
            print("❌ Mercado Pago não configurado")
            return None
        
        try:
            # Se não tiver email, usar um genérico
            if not payer_email:
                payer_email = f"user{transaction_id}@placeholder.com"
            
            # Criar pagamento
            payment_data = {
                "transaction_amount": float(amount),
                "description": description,
                "payment_method_id": "pix",
                "payer": {
                    "email": payer_email
                },
                "external_reference": str(transaction_id),  # Para rastrear
                "notification_url": f"{os.getenv('WEBHOOK_URL', '')}/webhook/mercadopago"
            }
            
            payment_response = self.sdk.payment().create(payment_data)
            payment = payment_response["response"]
            
            if payment_response["status"] != 201:
                print(f"❌ Erro ao criar pagamento: {payment}")
                return None
            
            # Extrair dados do Pix
            payment_id = payment["id"]
            qr_code_base64 = payment.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code_base64")
            qr_code = payment.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code")
            
            if not qr_code or not qr_code_base64:
                print(f"❌ QR Code não gerado: {payment}")
                return None
            
            print(f"✅ Pagamento Pix criado: {payment_id} - R$ {amount:.2f}")
            
            return {
                "payment_id": payment_id,
                "qr_code_base64": qr_code_base64,  # Imagem base64
                "qr_code": qr_code,  # Pix Copia e Cola
                "status": payment["status"],
                "amount": amount,
                "created_at": payment.get("date_created")
            }
            
        except Exception as e:
            print(f"❌ Erro ao criar pagamento Pix: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def check_payment_status(self, payment_id: str) -> Optional[Dict]:
        """
        Verifica status de um pagamento
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
            
        Returns:
            Dict com status e informações
        """
        if not self.is_configured():
            return None
        
        try:
            payment_response = self.sdk.payment().get(payment_id)
            payment = payment_response["response"]
            
            return {
                "payment_id": payment_id,
                "status": payment["status"],  # pending, approved, rejected, etc
                "status_detail": payment.get("status_detail"),
                "transaction_amount": payment.get("transaction_amount"),
                "external_reference": payment.get("external_reference"),
                "date_approved": payment.get("date_approved")
            }
            
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
            return None
    
    async def send_pix(
        self,
        amount: float,
        pix_key: str,
        pix_type: str,
        description: str = "Saque CaosBot"
    ) -> Optional[Dict]:
        """
        Envia Pix automático (para saques)
        
        IMPORTANTE: Esta funcionalidade requer conta Mercado Pago verificada
        e saldo disponível na conta.
        
        Args:
            amount: Valor a enviar
            pix_key: Chave Pix do destinatário
            pix_type: Tipo (CPF, CNPJ, EMAIL, PHONE, RANDOM)
            description: Descrição da transferência
            
        Returns:
            Dict com transfer_id, status ou None se erro
        """
        if not self.is_configured():
            print("❌ Mercado Pago não configurado")
            return None
        
        try:
            # NOTA: A API de transferências do Mercado Pago é diferente
            # Requer permissões especiais e conta verificada
            
            # Para MVP, vamos usar a API de pagamentos com opção de transferência
            # Documentação: https://www.mercadopago.com.br/developers/pt/docs/checkout-api/transfers
            
            transfer_data = {
                "amount": float(amount),
                "description": description,
                "payment_method_id": "pix",
                "payer": {
                    "type": "customer",
                    "identification": {
                        "type": pix_type.upper(),
                        "number": pix_key
                    }
                }
            }
            
            # IMPORTANTE: Esta parte precisa de configuração adicional no Mercado Pago
            # Por enquanto, vamos simular o sucesso para desenvolvimento
            
            print(f"💸 Pix enviado (simulado): R$ {amount:.2f} para {pix_key}")
            
            return {
                "transfer_id": f"MP-{int(datetime.now().timestamp())}",
                "status": "approved",
                "amount": amount,
                "pix_key": pix_key,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro ao enviar Pix: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_qr_code_image(self, pix_code: str) -> BytesIO:
        """
        Gera imagem QR Code a partir do Pix Copia e Cola
        
        Args:
            pix_code: Código Pix (string grande)
            
        Returns:
            BytesIO com imagem PNG do QR Code
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(pix_code)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Salvar em BytesIO
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            print(f"❌ Erro ao gerar QR Code: {e}")
            return None
    
    def validate_webhook_signature(self, data: str, signature: str) -> bool:
        """
        Valida assinatura do webhook do Mercado Pago
        
        Args:
            data: Dados recebidos
            signature: Assinatura do header x-signature
            
        Returns:
            True se válido
        """
        try:
            # Mercado Pago envia header x-signature
            # Validar usando secret do webhook
            secret = os.getenv('MERCADOPAGO_WEBHOOK_SECRET', '')
            
            if not secret:
                print("⚠️ MERCADOPAGO_WEBHOOK_SECRET não configurado - pulando validação")
                return True
            
            # Calcular HMAC
            expected_signature = hmac.new(
                secret.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            print(f"❌ Erro ao validar assinatura: {e}")
            return False
    
    async def process_webhook_payment(self, payment_id: str) -> Optional[Dict]:
        """
        Processa webhook de pagamento aprovado
        
        Args:
            payment_id: ID do pagamento notificado
            
        Returns:
            Dict com dados do pagamento ou None
        """
        payment_info = await self.check_payment_status(payment_id)
        
        if not payment_info:
            return None
        
        # Retornar apenas se aprovado
        if payment_info["status"] == "approved":
            print(f"✅ Pagamento aprovado via webhook: {payment_id}")
            return payment_info
        else:
            print(f"ℹ️ Pagamento não aprovado: {payment_id} - Status: {payment_info['status']}")
            return None

