-- =====================================================
-- TESTE SIMPLIFICADO - SISTEMA MICRO SAAS
-- =====================================================
-- Opção 1: Usa produto existente
-- Opção 2: Torna product_id nullable temporariamente
-- =====================================================

-- =====================================================
-- PASSO 1: VERIFICAR PRODUTOS EXISTENTES
-- =====================================================
-- Execute este SELECT primeiro para ver se já tem algum produto

SELECT 
    id AS "ID do Produto",
    guild_id AS "Guild ID",
    name AS "Nome",
    price AS "Preço",
    created_at AS "Criado em"
FROM products
WHERE guild_id = 1300173398982393937
ORDER BY created_at DESC
LIMIT 5;

-- ✅ Se retornar produtos: anote o ID e use no PASSO 3
-- ❌ Se retornar vazio: execute o PASSO 2 primeiro


-- =====================================================
-- PASSO 2: TORNAR product_id OPCIONAL (TEMPORÁRIO)
-- =====================================================
-- Execute SOMENTE se não tiver produtos criados
-- Isso permite criar transações de teste sem produto

ALTER TABLE transactions 
ALTER COLUMN product_id DROP NOT NULL;

-- ✅ Agora podemos criar transações de teste sem produto


-- =====================================================
-- PASSO 3: SIMULAR VENDA DE R$ 100,00
-- =====================================================
-- Escolha uma das opções abaixo:

-- OPÇÃO A: Se você TEM um produto (substitua 123 pelo ID real)
-- --------------------------------------------------------

DO $$
DECLARE
    v_transaction_id INTEGER;
    v_guild_id BIGINT := 1300173398982393937;
    v_user_id BIGINT := 784058182515425310;
    v_product_id INTEGER := 123; -- ⚠️ SUBSTITUA pelo ID do seu produto
    v_amount DECIMAL := 100.00;
    v_platform_fee DECIMAL := 0.80;
    v_net_amount DECIMAL := 99.20;
BEGIN
    RAISE NOTICE '🚀 Iniciando teste de venda com produto...';
    
    -- Criar transação
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
        v_amount,
        'approved',
        'TEST-VENDA-' || floor(random() * 10000)::text,
        'mercadopago',
        v_platform_fee
    ) RETURNING id INTO v_transaction_id;
    
    RAISE NOTICE '✅ Transação criada: ID %', v_transaction_id;
    
    -- Creditar carteira
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
        platform_fees_paid = guild_wallets.platform_fees_paid + v_platform_fee;
    
    RAISE NOTICE '✅ Carteira creditada: R$ %.2f', v_net_amount;
    
    -- Registrar movimentação
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
        'Venda teste - Sistema SaaS',
        v_transaction_id
    );
    
    -- Registrar taxa
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
    
    RAISE NOTICE '✅ Taxa registrada: R$ 0.80';
    RAISE NOTICE '';
    RAISE NOTICE '🎉 TESTE COMPLETO!';
    RAISE NOTICE '💰 Valor: R$ 100.00 | Taxa: R$ 0.80 | Líquido: R$ 99.20';
    RAISE NOTICE '🎮 Digite /saldo no Discord!';
END $$;


-- OPÇÃO B: Se você NÃO TEM produto (executou o PASSO 2)
-- --------------------------------------------------------

/*
DO $$
DECLARE
    v_transaction_id INTEGER;
    v_guild_id BIGINT := 1300173398982393937;
    v_user_id BIGINT := 784058182515425310;
    v_amount DECIMAL := 100.00;
    v_platform_fee DECIMAL := 0.80;
    v_net_amount DECIMAL := 99.20;
BEGIN
    RAISE NOTICE '🚀 Iniciando teste de venda SEM produto...';
    
    -- Criar transação sem produto
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
        NULL, -- Sem produto
        v_amount,
        'approved',
        'TEST-VENDA-' || floor(random() * 10000)::text,
        'mercadopago',
        v_platform_fee
    ) RETURNING id INTO v_transaction_id;
    
    RAISE NOTICE '✅ Transação criada: ID %', v_transaction_id;
    
    -- Creditar carteira
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
        platform_fees_paid = guild_wallets.platform_fees_paid + v_platform_fee;
    
    RAISE NOTICE '✅ Carteira creditada: R$ %.2f', v_net_amount;
    
    -- Registrar movimentação
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
        'Venda teste - Sistema SaaS (sem produto)',
        v_transaction_id
    );
    
    -- Registrar taxa
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
    
    RAISE NOTICE '✅ Taxa registrada: R$ 0.80';
    RAISE NOTICE '';
    RAISE NOTICE '🎉 TESTE COMPLETO!';
    RAISE NOTICE '💰 Valor: R$ 100.00 | Taxa: R$ 0.80 | Líquido: R$ 99.20';
    RAISE NOTICE '🎮 Digite /saldo no Discord!';
END $$;
*/


-- =====================================================
-- PASSO 4: VERIFICAR SALDO
-- =====================================================

SELECT 
    guild_id,
    balance_available AS "💰 Saldo Disponível",
    balance_pending AS "⏳ Pendente",
    total_earned AS "📈 Total Ganho",
    total_withdrawn AS "💸 Total Sacado",
    platform_fees_paid AS "💳 Taxas Pagas"
FROM guild_wallets
WHERE guild_id = 1300173398982393937;


-- =====================================================
-- 🆘 SE PRECISAR CRIAR UM PRODUTO PELO DISCORD
-- =====================================================
-- Use este comando no seu servidor Discord:
--
-- /admin_criar_produto
--   nome: Produto Teste
--   preco: 10
--   descricao: Produto para testes
--   estoque: 999
--
-- Depois execute o PASSO 1 novamente para pegar o ID

