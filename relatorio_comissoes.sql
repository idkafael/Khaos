-- =====================================================
-- RELATÓRIO DE COMISSÕES - MICRO SAAS
-- =====================================================
-- Execute este SQL no Supabase para ver suas comissões
-- =====================================================

-- 📊 RESUMO GERAL DE COMISSÕES
SELECT 
    '💰 RESUMO DE COMISSÕES' AS "Relatório",
    COUNT(*) AS "Total de Vendas",
    SUM(platform_fee) AS "💵 Comissões de Venda (R$ 0,80)",
    COALESCE((
        SELECT SUM(fee_amount) 
        FROM withdrawal_requests 
        WHERE status = 'completed'
    ), 0) AS "💸 Comissões de Saque (3%)",
    SUM(platform_fee) + COALESCE((
        SELECT SUM(fee_amount) 
        FROM withdrawal_requests 
        WHERE status = 'completed'
    ), 0) AS "💎 TOTAL GANHO"
FROM transactions
WHERE status = 'approved'
  AND platform_fee > 0;


-- =====================================================
-- 📈 COMISSÕES POR DIA (ÚLTIMOS 7 DIAS)
-- =====================================================

SELECT 
    DATE(created_at) AS "📅 Data",
    COUNT(*) AS "Vendas",
    SUM(platform_fee) AS "💰 Comissão Venda",
    SUM(amount) AS "💵 Volume Total"
FROM transactions
WHERE status = 'approved'
  AND created_at >= NOW() - INTERVAL '7 days'
  AND platform_fee > 0
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;


-- =====================================================
-- 🏆 TOP 10 SERVIDORES POR COMISSÃO GERADA
-- =====================================================

SELECT 
    guild_id AS "Server ID",
    COUNT(*) AS "Vendas",
    SUM(amount) AS "💵 Volume",
    SUM(platform_fee) AS "💰 Sua Comissão"
FROM transactions
WHERE status = 'approved'
  AND platform_fee > 0
GROUP BY guild_id
ORDER BY SUM(platform_fee) DESC
LIMIT 10;


-- =====================================================
-- 💸 HISTÓRICO DE SAQUES E COMISSÕES
-- =====================================================

SELECT 
    guild_id AS "Server ID",
    amount_requested AS "Valor Solicitado",
    fee_amount AS "💰 Sua Comissão (3%)",
    net_amount AS "Enviado ao Servidor",
    status AS "Status",
    requested_at AS "Data"
FROM withdrawal_requests
WHERE status = 'completed'
ORDER BY requested_at DESC
LIMIT 20;


-- =====================================================
-- 📊 ESTATÍSTICAS FINANCEIRAS COMPLETAS
-- =====================================================

SELECT 
    'Vendas Processadas' AS "Métrica",
    COUNT(*)::TEXT AS "Valor"
FROM transactions
WHERE status = 'approved' AND platform_fee > 0

UNION ALL

SELECT 
    'Volume Total de Vendas',
    'R$ ' || ROUND(SUM(amount)::NUMERIC, 2)::TEXT
FROM transactions
WHERE status = 'approved' AND platform_fee > 0

UNION ALL

SELECT 
    '💰 Total em Comissões de Venda',
    'R$ ' || ROUND(SUM(platform_fee)::NUMERIC, 2)::TEXT
FROM transactions
WHERE status = 'approved' AND platform_fee > 0

UNION ALL

SELECT 
    'Saques Processados',
    COUNT(*)::TEXT
FROM withdrawal_requests
WHERE status = 'completed'

UNION ALL

SELECT 
    '💸 Total em Comissões de Saque',
    'R$ ' || ROUND(SUM(fee_amount)::NUMERIC, 2)::TEXT
FROM withdrawal_requests
WHERE status = 'completed'

UNION ALL

SELECT 
    '💎 LUCRO TOTAL',
    'R$ ' || ROUND((
        SELECT COALESCE(SUM(platform_fee), 0) FROM transactions WHERE status = 'approved' AND platform_fee > 0
    ) + (
        SELECT COALESCE(SUM(fee_amount), 0) FROM withdrawal_requests WHERE status = 'completed'
    ), 2)::TEXT;

