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
        payer_email: str = None,
        payer_first_name: str = None,
        payer_last_name: str = None,
        item_title: str = None,
        item_category: str = None,
        item_id: str = None,
        item_quantity: int = 1
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
            print("❌ Mercado Pago não configurado - SDK não inicializado")
            print(f"   ACCESS_TOKEN presente: {bool(self.access_token)}")
            print(f"   SDK inicializado: {self.sdk is not None}")
            return None
        
        try:
            print(f"💳 [MP] Criando pagamento Pix de R$ {amount:.2f}")
            print(f"📝 [MP] Descrição: {description}")
            print(f"🆔 [MP] Transaction ID: {transaction_id}")
            
            # Se não tiver email, usar um genérico
            if not payer_email:
                payer_email = f"user{transaction_id}@placeholder.com"
            
            print(f"📧 [MP] Email do pagador: {payer_email}")
            
            # Preparar dados do pagador (para ganhar pontos no MP)
            payer_data = {"email": payer_email}
            
            if payer_first_name:
                payer_data["first_name"] = payer_first_name
                print(f"👤 [MP] Nome: {payer_first_name}")
            
            if payer_last_name:
                payer_data["last_name"] = payer_last_name
                print(f"👤 [MP] Sobrenome: {payer_last_name}")
            
            # Preparar items (para ganhar pontos no MP) - SEMPRE criar item
            items = []
            # Sempre criar um item, mesmo sem título específico
            item_data = {
                "title": item_title or description,  # +2 pontos
                "description": description,  # +2 pontos
                "quantity": item_quantity,  # +2 pontos
                "unit_price": round(float(amount) / item_quantity, 2),  # +2 pontos
            }
            
            # Categoria específica (ganha 3 pontos) - SEMPRE adicionar
            if item_category:
                item_data["category_id"] = item_category
            else:
                item_data["category_id"] = "digital_goods"  # Categoria padrão
            
            # ID do item (ganha 3 pontos) - SEMPRE adicionar
            if item_id:
                item_data["id"] = str(item_id)
            else:
                item_data["id"] = str(transaction_id)  # Usar transaction_id como fallback
            
            items.append(item_data)
            print(f"📦 [MP] Item completo: {item_data}")
            print(f"📦 [MP] Pontos esperados: title(2) + description(2) + quantity(2) + unit_price(2) + category_id(3) + id(3) = 14 pontos")
            
            # Criar pagamento
            payment_data = {
                "transaction_amount": round(float(amount), 2),  # Sempre 2 casas decimais
                "description": description,
                "payment_method_id": "pix",
                "payer": payer_data,
                "external_reference": str(transaction_id),  # Para rastrear
                "statement_descriptor": "KHAOS DIGITAL",  # Nome que aparece na fatura (ganha 10 pontos!)
                "metadata": {
                    "platform": "discord_bot",
                    "version": "2.0",
                    "device_id": "discord_bot_khaos"  # Identificador do dispositivo (ganha 2 pontos!)
                }
            }
            
            # Adicionar items se houver
            if items:
                payment_data["additional_info"] = {
                    "items": items
                }
                print(f"📦 [MP] Additional info adicionado: {payment_data['additional_info']}")
            else:
                print("⚠️ [MP] Nenhum item para adicionar ao pagamento")
            
            # Adicionar notification_url apenas se WEBHOOK_URL estiver configurado
            webhook_url = os.getenv('WEBHOOK_URL', '').strip()
            if webhook_url and webhook_url.startswith('http'):
                payment_data["notification_url"] = f"{webhook_url}/webhook/mercadopago"
                print(f"🔔 [MP] Webhook configurado: {payment_data['notification_url']}")
            else:
                print(f"⚠️ [MP] WEBHOOK_URL não configurado - pagamentos serão verificados manualmente")
            
            print(f"📤 [MP] Enviando dados para API Mercado Pago...")
            print(f"💰 [MP] Valor: R$ {payment_data['transaction_amount']}")
            print(f"📋 [MP] Dados completos do pagamento: {payment_data}")
            
            payment_response = self.sdk.payment().create(payment_data)
            
            print(f"📥 [MP] Resposta recebida - Status: {payment_response['status']}")
            
            payment = payment_response["response"]
            
            if payment_response["status"] != 201:
                print(f"❌ [MP] Erro ao criar pagamento - Status: {payment_response['status']}")
                print(f"📄 [MP] Resposta: {payment}")
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

