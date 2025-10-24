-- ========================================
-- SISTEMA DE LOGS - Setup SQL
-- ========================================
-- Execute este SQL no Supabase SQL Editor
-- Adiciona campos de configuração de logs
-- ========================================

-- Adicionar campos de log na tabela guild_config
ALTER TABLE guild_config 
ADD COLUMN IF NOT EXISTS log_channel_id BIGINT,
ADD COLUMN IF NOT EXISTS log_events TEXT[];

-- Comentários para documentação
COMMENT ON COLUMN guild_config.log_channel_id IS 'ID do canal do Discord para enviar logs';
COMMENT ON COLUMN guild_config.log_events IS 'Array de event_ids para logar (vazio = logar tudo)';

-- ========================================
-- EVENTOS DISPONÍVEIS
-- ========================================
-- payment_confirmed: Pagamentos confirmados
-- product_delivered: Produtos entregues  
-- payment_generated: Pagamentos gerados
-- ticket_created: Tickets de compra criados
-- support_ticket_created: Tickets de suporte criados
-- ticket_closed: Tickets fechados
-- coupon_used: Cupons utilizados
-- vip_activated: VIP ativado
-- vip_expired: VIP expirado
-- stock_added: Estoque adicionado
-- product_created: Produtos criados
-- ========================================

-- Exemplo de configuração:
-- UPDATE guild_config 
-- SET log_channel_id = 123456789,
--     log_events = ARRAY['payment_confirmed', 'product_delivered']
-- WHERE guild_id = 987654321;

-- Verificar configurações de log:
SELECT guild_id, guild_name, log_channel_id, log_events
FROM guild_config
WHERE log_channel_id IS NOT NULL;

