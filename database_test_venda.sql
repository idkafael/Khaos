-- =====================================================
-- TESTE DE VENDA - SISTEMA MICRO SAAS (CORRIGIDO)
-- =====================================================
-- Execute este SQL completo no Supabase SQL Editor
-- Ele vai criar um produto fake e depois simular uma venda
-- =====================================================

DO $$
DECLARE
    v_transaction_id INTEGER;
    v_product_id INTEGER;
    v_guild_id BIGINT := 1300173398982393937; -- Seu servidor "Khaos Community"
    v_user_id BIGINT := 784058182515425310; -- Seu user ID
    v_amount DECIMAL := 100.00;
    v_platform_fee DECIMAL := 0.80;
    v_net_amount DECIMAL := 99.20;
BEGIN
    RAISE NOTICE '🚀 Iniciando teste de venda...';
    
    -- ============================================
    -- 1️⃣ CRIAR PRODUTO FAKE (se não existir)
    -- ============================================
    INSERT INTO products (
        guild_id,
        name,
        description,
        price,
        type,
        stock,
        active
    ) VALUES (
        v_guild_id,
        'Produto Teste SaaS',
        'Produto criado automaticamente para testar o sistema de carteira',
        v_amount,
        'digital',
        999,
        true
    )
    ON CONFLICT (id) DO NOTHING
    RETURNING id INTO v_product_id;
    
    -- Se o produto já existia, buscar o ID
    IF v_product_id IS NULL THEN
        SELECT id INTO v_product_id 
        FROM products 
        WHERE guild_id = v_guild_id 
        LIMIT 1;
    END IF;
    
    RAISE NOTICE '✅ Produto ID: %', v_product_id;
    
    -- ============================================
    -- 2️⃣ CRIAR TRANSAÇÃO DE VENDA
    -- ============================================
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
        v_product_id, -- Agora usa o ID do produto criado
        v_amount,
        'approved',
        'TEST-VENDA-' || floor(random() * 1000)::text, -- ID único
        'mercadopago',
        v_platform_fee
    ) RETURNING id INTO v_transaction_id;
    
    RAISE NOTICE '✅ Transação criada: ID %', v_transaction_id;
    
    -- ============================================
    -- 3️⃣ CREDITAR CARTEIRA DO SERVIDOR
    -- ============================================
    -- Valor líquido: R$ 100,00 - R$ 0,80 = R$ 99,20
    
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
    
    -- ============================================
    -- 4️⃣ REGISTRAR MOVIMENTAÇÃO NA CARTEIRA
    -- ============================================
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
        'Venda teste - ' || 'Produto Teste SaaS',
        v_transaction_id
    );
    
    RAISE NOTICE '✅ Movimentação registrada na carteira';
    
    -- ============================================
    -- 5️⃣ REGISTRAR TAXA NA PLATAFORMA
    -- ============================================
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
        'Taxa fixa por venda (R$ 0,80)'
    );
    
    RAISE NOTICE '✅ Taxa registrada: R$ %.2f', v_platform_fee;
    
    -- ============================================
    -- 🎉 RESUMO FINAL
    -- ============================================
    RAISE NOTICE '';
    RAISE NOTICE '════════════════════════════════════';
    RAISE NOTICE '🎉 TESTE COMPLETO!';
    RAISE NOTICE '════════════════════════════════════';
    RAISE NOTICE '💰 Valor da venda: R$ %.2f', v_amount;
    RAISE NOTICE '💳 Taxa da plataforma: R$ %.2f', v_platform_fee;
    RAISE NOTICE '💵 Creditado na carteira: R$ %.2f', v_net_amount;
    RAISE NOTICE '';
    RAISE NOTICE '🎮 Agora digite /saldo no Discord para ver!';
    RAISE NOTICE '════════════════════════════════════';
    
END $$;

-- =====================================================
-- 📊 VERIFICAR SALDO ATUAL
-- =====================================================

SELECT 
    guild_id,
    balance_available AS "💰 Saldo Disponível",
    balance_pending AS "⏳ Saldo Pendente",
    total_earned AS "📈 Total Ganho",
    total_withdrawn AS "💸 Total Sacado",
    platform_fees_paid AS "💳 Taxas Pagas",
    (total_earned - total_withdrawn - platform_fees_paid) AS "💎 Lucro Líquido"
FROM guild_wallets
WHERE guild_id = 1300173398982393937;

