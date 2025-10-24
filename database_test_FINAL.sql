-- =====================================================
-- TESTE FINAL - SISTEMA MICRO SAAS (ESTRUTURA CORRETA)
-- =====================================================
-- Execute este SQL após criar um produto no Discord
-- Substitua o ID do produto pela linha 15
-- =====================================================

DO $$
DECLARE
    v_transaction_id INTEGER;
    v_guild_id BIGINT := 1300173398982393937;
    v_user_id BIGINT := 784058182515425310;
    v_product_id INTEGER := 999; -- ⚠️ SUBSTITUA PELO ID DO SEU PRODUTO
    v_gross_amount DECIMAL := 100.00; -- Valor da venda
    v_platform_fee DECIMAL := 0.80; -- Taxa fixa
    v_net_amount DECIMAL := 99.20; -- Valor líquido (100 - 0.80)
    v_current_balance DECIMAL := 0.00;
    v_new_balance DECIMAL := 0.00;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '🚀 TESTE DE VENDA - SISTEMA MICRO SAAS';
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '';
    
    -- ============================================
    -- 1️⃣ CRIAR TRANSAÇÃO DE VENDA
    -- ============================================
    RAISE NOTICE '1️⃣ Criando transação de venda...';
    
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
        v_product_id,
        v_gross_amount,
        'approved',
        'TEST-VENDA-' || floor(random() * 10000)::text,
        'mercadopago',
        v_platform_fee
    ) RETURNING id INTO v_transaction_id;
    
    RAISE NOTICE '   ✅ Transação criada: ID %', v_transaction_id;
    RAISE NOTICE '   💰 Valor: R$ %.2f', v_gross_amount;
    RAISE NOTICE '   💳 Taxa: R$ %.2f', v_platform_fee;
    RAISE NOTICE '   💵 Líquido: R$ %.2f', v_net_amount;
    RAISE NOTICE '';
    
    -- ============================================
    -- 2️⃣ BUSCAR SALDO ATUAL DA CARTEIRA
    -- ============================================
    RAISE NOTICE '2️⃣ Verificando saldo atual...';
    
    SELECT COALESCE(balance_available, 0) 
    INTO v_current_balance
    FROM guild_wallets
    WHERE guild_id = v_guild_id;
    
    IF v_current_balance IS NULL THEN
        v_current_balance := 0.00;
    END IF;
    
    v_new_balance := v_current_balance + v_net_amount;
    
    RAISE NOTICE '   💰 Saldo anterior: R$ %.2f', v_current_balance;
    RAISE NOTICE '   ➕ Creditando: R$ %.2f', v_net_amount;
    RAISE NOTICE '   💰 Novo saldo: R$ %.2f', v_new_balance;
    RAISE NOTICE '';
    
    -- ============================================
    -- 3️⃣ CREDITAR CARTEIRA DO SERVIDOR
    -- ============================================
    RAISE NOTICE '3️⃣ Creditando carteira...';
    
    INSERT INTO guild_wallets (
        guild_id, 
        balance_available, 
        balance_pending, 
        total_earned, 
        total_withdrawn, 
        platform_fees_paid
    ) VALUES (
        v_guild_id,
        v_net_amount,
        0.00,
        v_net_amount,
        0.00,
        v_platform_fee
    )
    ON CONFLICT (guild_id) DO UPDATE SET
        balance_available = guild_wallets.balance_available + v_net_amount,
        total_earned = guild_wallets.total_earned + v_net_amount,
        platform_fees_paid = guild_wallets.platform_fees_paid + v_platform_fee,
        updated_at = NOW();
    
    RAISE NOTICE '   ✅ Carteira creditada!';
    RAISE NOTICE '';
    
    -- ============================================
    -- 4️⃣ REGISTRAR MOVIMENTAÇÃO NA CARTEIRA
    -- ============================================
    RAISE NOTICE '4️⃣ Registrando movimentação...';
    
    INSERT INTO wallet_transactions (
        guild_id,
        transaction_id,
        type,
        gross_amount,
        platform_fee,
        net_amount,
        balance_after,
        description
    ) VALUES (
        v_guild_id,
        v_transaction_id,
        'credit_sale', -- ✅ Nome correto da coluna
        v_gross_amount,
        v_platform_fee,
        v_net_amount,
        v_new_balance,
        'Venda teste - Sistema Micro SaaS'
    );
    
    RAISE NOTICE '   ✅ Movimentação registrada!';
    RAISE NOTICE '';
    
    -- ============================================
    -- 5️⃣ REGISTRAR TAXA NA PLATAFORMA
    -- ============================================
    RAISE NOTICE '5️⃣ Registrando taxa da plataforma...';
    
    INSERT INTO platform_fees (
        guild_id,
        transaction_id,
        fee_type,
        amount,
        description
    ) VALUES (
        v_guild_id,
        v_transaction_id,
        'sale_fixed', -- ✅ Taxa fixa de venda
        v_platform_fee,
        'Taxa fixa por venda (R$ 0,80)'
    );
    
    RAISE NOTICE '   ✅ Taxa registrada: R$ %.2f', v_platform_fee;
    RAISE NOTICE '';
    
    -- ============================================
    -- 🎉 RESUMO FINAL
    -- ============================================
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '🎉 TESTE COMPLETO COM SUCESSO!';
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '📊 RESUMO DA OPERAÇÃO:';
    RAISE NOTICE '   💰 Valor da venda: R$ %.2f', v_gross_amount;
    RAISE NOTICE '   💳 Taxa da plataforma: R$ %.2f', v_platform_fee;
    RAISE NOTICE '   💵 Creditado na carteira: R$ %.2f', v_net_amount;
    RAISE NOTICE '   💎 Novo saldo: R$ %.2f', v_new_balance;
    RAISE NOTICE '';
    RAISE NOTICE '🎮 Digite /saldo no Discord para conferir!';
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '';
    
END $$;


-- =====================================================
-- 📊 VERIFICAR SALDO ATUAL
-- =====================================================

SELECT 
    '💰 SALDO DA CARTEIRA' AS "Status",
    guild_id AS "Guild ID",
    balance_available AS "💰 Disponível",
    balance_pending AS "⏳ Pendente",
    total_earned AS "📈 Total Ganho",
    total_withdrawn AS "💸 Total Sacado",
    platform_fees_paid AS "💳 Taxas Pagas",
    (total_earned - total_withdrawn - platform_fees_paid) AS "💎 Lucro Líquido"
FROM guild_wallets
WHERE guild_id = 1300173398982393937;


-- =====================================================
-- 📜 VERIFICAR HISTÓRICO DE MOVIMENTAÇÕES
-- =====================================================

SELECT 
    id AS "ID",
    CASE 
        WHEN type = 'credit_sale' THEN '💰 Venda'
        WHEN type = 'debit_withdrawal' THEN '💸 Saque'
        WHEN type = 'fee_sale' THEN '💳 Taxa Venda'
        WHEN type = 'fee_withdrawal' THEN '💳 Taxa Saque'
        ELSE type
    END AS "Tipo",
    gross_amount AS "Valor Bruto",
    platform_fee AS "Taxa",
    net_amount AS "Valor Líquido",
    balance_after AS "Saldo Após",
    description AS "Descrição",
    created_at AS "Data"
FROM wallet_transactions
WHERE guild_id = 1300173398982393937
ORDER BY created_at DESC
LIMIT 10;


-- =====================================================
-- 💳 VERIFICAR TAXAS COBRADAS
-- =====================================================

SELECT 
    id AS "ID",
    CASE 
        WHEN fee_type = 'sale_fixed' THEN '💰 Venda (Fixo)'
        WHEN fee_type = 'withdrawal_percent' THEN '💸 Saque (3%)'
        ELSE fee_type
    END AS "Tipo de Taxa",
    amount AS "Valor",
    description AS "Descrição",
    created_at AS "Data"
FROM platform_fees
WHERE guild_id = 1300173398982393937
ORDER BY created_at DESC;

