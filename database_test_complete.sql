-- =====================================================
-- SCRIPT DE TESTE COMPLETO - SISTEMA MICRO SAAS
-- =====================================================
-- Execute cada seção EM ORDEM, uma por vez
-- Copie e cole no SQL Editor do Supabase
-- =====================================================

-- =====================================================
-- SEÇÃO 1: VERIFICAR SE TABELAS EXISTEM
-- =====================================================
-- Este SELECT deve retornar 4 linhas (as 4 tabelas novas)

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('guild_wallets', 'wallet_transactions', 'withdrawal_requests', 'platform_fees')
ORDER BY table_name;

-- ✅ Resultado esperado: 4 tabelas listadas


-- =====================================================
-- SEÇÃO 2: VERIFICAR SE COLUNAS FORAM ADICIONADAS
-- =====================================================
-- Este SELECT deve retornar 3 linhas (as 3 novas colunas)

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'transactions' 
  AND column_name IN ('guild_id', 'gateway_used', 'platform_fee')
ORDER BY column_name;

-- ✅ Resultado esperado: 
-- guild_id | bigint
-- gateway_used | character varying
-- platform_fee | numeric


-- =====================================================
-- SEÇÃO 3: SIMULAR UMA VENDA DE R$ 100,00
-- =====================================================
-- Esta venda vai:
-- 1. Criar uma transaction na tabela transactions
-- 2. Creditar R$ 99,20 na carteira (R$ 100 - R$ 0,80 de taxa)
-- 3. Registrar a taxa de R$ 0,80 na tabela platform_fees

DO $$
DECLARE
    v_transaction_id INTEGER;
    v_guild_id BIGINT := 1300173398982393937; -- Seu servidor "Khaos Community"
    v_user_id BIGINT := 784058182515425310; -- Seu user ID
    v_amount DECIMAL := 100.00;
    v_platform_fee DECIMAL := 0.80;
    v_net_amount DECIMAL := 99.20;
BEGIN
    -- 1️⃣ Criar transação de venda
    INSERT INTO transactions (
        guild_id, 
        user_id, 
        product_id, 
        amount, 
        status, 
        payment_id, 
        gateway_used, 
        platform_fee
    ) VALUES (
        v_guild_id,
        v_user_id,
        1, -- ID produto fake (pode ser qualquer número)
        v_amount,
        'approved',
        'TEST-VENDA-001',
        'mercadopago',
        v_platform_fee
    ) RETURNING id INTO v_transaction_id;
    
    RAISE NOTICE '✅ Transação criada: ID %', v_transaction_id;
    
    -- 2️⃣ Creditar carteira do servidor (R$ 100 - R$ 0,80 = R$ 99,20)
    INSERT INTO guild_wallets (
        guild_id, 
        balance_available, 
        balance_pending, 
        total_earned, 
        total_withdrawn, 
        platform_fees_paid
    ) VALUES (
        v_guild_id,
        v_net_amount, -- R$ 99,20 disponível
        0.00,
        v_net_amount, -- R$ 99,20 ganho total
        0.00,
        v_platform_fee -- R$ 0,80 de taxa paga
    )
    ON CONFLICT (guild_id) DO UPDATE SET
        balance_available = guild_wallets.balance_available + v_net_amount,
        total_earned = guild_wallets.total_earned + v_net_amount,
        platform_fees_paid = guild_wallets.platform_fees_paid + v_platform_fee;
    
    RAISE NOTICE '✅ Carteira creditada: R$ %.2f (líquido)', v_net_amount;
    
    -- 3️⃣ Registrar movimentação na wallet_transactions
    INSERT INTO wallet_transactions (
        guild_id,
        transaction_type,
        amount,
        fee_charged,
        description,
        reference_id
    ) VALUES (
        v_guild_id,
        'sale',
        v_net_amount,
        v_platform_fee,
        'Venda teste - Produto Fake',
        v_transaction_id
    );
    
    RAISE NOTICE '✅ Movimentação registrada na carteira';
    
    -- 4️⃣ Registrar taxa na platform_fees
    INSERT INTO platform_fees (
        guild_id,
        transaction_id,
        fee_type,
        amount,
        description
    ) VALUES (
        v_guild_id,
        v_transaction_id,
        'sale_fee',
        v_platform_fee,
        'Taxa fixa por venda'
    );
    
    RAISE NOTICE '✅ Taxa registrada: R$ %.2f', v_platform_fee;
    RAISE NOTICE '🎉 TESTE COMPLETO! Verifique o saldo no Discord com /saldo';
END $$;

-- ✅ Resultado esperado no log:
-- NOTICE: ✅ Transação criada: ID 123
-- NOTICE: ✅ Carteira creditada: R$ 99.20 (líquido)
-- NOTICE: ✅ Movimentação registrada na carteira
-- NOTICE: ✅ Taxa registrada: R$ 0.80
-- NOTICE: 🎉 TESTE COMPLETO! Verifique o saldo no Discord com /saldo


-- =====================================================
-- SEÇÃO 4: VERIFICAR SALDO DA CARTEIRA
-- =====================================================
-- Este SELECT mostra o saldo atual do seu servidor

SELECT 
    guild_id,
    balance_available AS "Saldo Disponível",
    balance_pending AS "Saldo Pendente",
    total_earned AS "Total Ganho",
    total_withdrawn AS "Total Sacado",
    platform_fees_paid AS "Taxas Pagas",
    created_at AS "Criado em"
FROM guild_wallets
WHERE guild_id = 1300173398982393937
ORDER BY created_at DESC;

-- ✅ Resultado esperado:
-- Saldo Disponível: 99.20
-- Saldo Pendente: 0.00
-- Total Ganho: 99.20
-- Total Sacado: 0.00
-- Taxas Pagas: 0.80


-- =====================================================
-- SEÇÃO 5: VERIFICAR HISTÓRICO DE MOVIMENTAÇÕES
-- =====================================================
-- Este SELECT mostra todas as movimentações da carteira

SELECT 
    id,
    transaction_type AS "Tipo",
    amount AS "Valor",
    fee_charged AS "Taxa",
    description AS "Descrição",
    created_at AS "Data"
FROM wallet_transactions
WHERE guild_id = 1300173398982393937
ORDER BY created_at DESC
LIMIT 10;

-- ✅ Resultado esperado: 1 linha mostrando a venda de R$ 99,20


-- =====================================================
-- SEÇÃO 6: VERIFICAR TAXAS COBRADAS
-- =====================================================
-- Este SELECT mostra todas as taxas que a plataforma cobrou

SELECT 
    id,
    fee_type AS "Tipo de Taxa",
    amount AS "Valor",
    description AS "Descrição",
    created_at AS "Data"
FROM platform_fees
WHERE guild_id = 1300173398982393937
ORDER BY created_at DESC;

-- ✅ Resultado esperado: 1 linha mostrando taxa de R$ 0,80


-- =====================================================
-- 🧹 SEÇÃO 7: LIMPAR DADOS DE TESTE (OPCIONAL)
-- =====================================================
-- ⚠️ Execute SOMENTE se quiser resetar os testes

-- DELETE FROM wallet_transactions WHERE guild_id = 1300173398982393937;
-- DELETE FROM platform_fees WHERE guild_id = 1300173398982393937;
-- DELETE FROM guild_wallets WHERE guild_id = 1300173398982393937;
-- DELETE FROM transactions WHERE guild_id = 1300173398982393937 AND payment_id LIKE 'TEST-%';

-- RAISE NOTICE '🧹 Dados de teste limpos!';

