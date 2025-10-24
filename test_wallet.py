"""
Teste do Sistema de Carteira Virtual
Execute: python test_wallet.py
"""

import asyncio
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

from models.wallet_model import WalletModel
from models.transaction_model import TransactionModel

async def test_credit_wallet():
    print("🧪 Iniciando teste de crédito de carteira...")
    
    wallet_model = WalletModel()
    transaction_model = TransactionModel()
    
    # ID do seu servidor "Khaos Community"
    guild_id = 1300173398982393937
    
    # 1. Criar transação fake
    print("\n📝 Criando transação de teste...")
    transaction_data = {
        'guild_id': guild_id,
        'user_id': 784058182515425310,
        'product_id': 1,
        'amount': 100.00,
        'status': 'approved',
        'payment_id': 'TEST-PAYMENT-001',
        'gateway_used': 'mercadopago',
        'platform_fee': 0.80
    }
    
    transaction = await transaction_model.create_transaction(transaction_data)
    
    if not transaction:
        print("❌ Erro ao criar transação")
        return
    
    print(f"✅ Transação criada: ID {transaction['id']}")
    
    # 2. Creditar carteira (desconta R$ 0,80)
    print("\n💰 Creditando carteira...")
    success = await wallet_model.credit_wallet(
        guild_id=guild_id,
        amount=100.00,
        transaction_id=transaction['id'],
        description="Venda de teste - Produto Teste"
    )
    
    if success:
        print("✅ Carteira creditada com sucesso!")
    else:
        print("❌ Erro ao creditar carteira")
        return
    
    # 3. Verificar saldo
    print("\n📊 Verificando saldo...")
    stats = await wallet_model.get_wallet_stats(guild_id)
    
    print(f"\n💵 Saldo Disponível: R$ {stats['balance_available']:.2f}")
    print(f"📈 Total Ganho: R$ {stats['total_earned']:.2f}")
    print(f"💳 Taxas Pagas: R$ {stats['platform_fees_paid']:.2f}")
    
    # Validação
    expected_balance = 99.20  # R$ 100 - R$ 0,80
    if abs(stats['balance_available'] - expected_balance) < 0.01:
        print("\n✅ TESTE PASSOU! Saldo correto: R$ 99,20")
    else:
        print(f"\n❌ TESTE FALHOU! Esperado: R$ 99,20, Recebido: R$ {stats['balance_available']:.2f}")
    
    print("\n✅ Teste completo! Verifique no Discord com /saldo")

if __name__ == "__main__":
    asyncio.run(test_credit_wallet())

