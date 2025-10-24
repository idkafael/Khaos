"""
Script de teste para verificar se Mercado Pago está funcionando
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Verificar se variáveis existem
access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
public_key = os.getenv('MERCADOPAGO_PUBLIC_KEY')

print("=" * 50)
print("🔍 TESTE DE CONFIGURAÇÃO MERCADO PAGO")
print("=" * 50)
print()

if not access_token:
    print("❌ MERCADOPAGO_ACCESS_TOKEN não encontrado no .env")
else:
    print(f"✅ ACCESS_TOKEN encontrado: {access_token[:20]}...")

if not public_key:
    print("❌ MERCADOPAGO_PUBLIC_KEY não encontrado no .env")
else:
    print(f"✅ PUBLIC_KEY encontrado: {public_key[:20]}...")

print()

if access_token:
    print("🔄 Testando SDK do Mercado Pago...")
    try:
        import mercadopago
        sdk = mercadopago.SDK(access_token)
        print("✅ SDK inicializado com sucesso!")
        
        # Testar criando um pagamento de teste
        print("\n🔄 Tentando criar pagamento Pix de teste (R$ 5,00)...")
        
        payment_data = {
            "transaction_amount": 5.00,
            "description": "Teste de Pagamento",
            "payment_method_id": "pix",
            "payer": {
                "email": "teste@teste.com"
            },
            "external_reference": "TEST-001"
        }
        
        result = sdk.payment().create(payment_data)
        
        print(f"\n📊 Status da resposta: {result['status']}")
        
        if result['status'] == 201:
            payment = result['response']
            payment_id = payment['id']
            qr_code_base64 = payment.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code_base64')
            qr_code = payment.get('point_of_interaction', {}).get('transaction_data', {}).get('qr_code')
            
            print(f"✅ Pagamento criado com sucesso!")
            print(f"   ID: {payment_id}")
            print(f"   QR Code base64: {'Presente' if qr_code_base64 else 'AUSENTE'}")
            print(f"   Pix Copia e Cola: {'Presente' if qr_code else 'AUSENTE'}")
            
            if qr_code:
                print(f"\n💳 Pix Copia e Cola (primeiros 50 chars):")
                print(f"   {qr_code[:50]}...")
        else:
            print(f"❌ Erro ao criar pagamento!")
            print(f"📄 Resposta completa:")
            print(result['response'])
            
    except ImportError:
        print("❌ Módulo 'mercadopago' não instalado!")
        print("   Execute: pip install mercadopago")
    except Exception as e:
        print(f"❌ Erro ao testar SDK: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️ Não é possível testar sem ACCESS_TOKEN")

print()
print("=" * 50)
print("✅ FIM DO TESTE")
print("=" * 50)

