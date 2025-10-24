-- ========================================
-- ADICIONAR CAMPOS DE LOG - CORREÇÃO RÁPIDA
-- ========================================
-- Execute este SQL no Supabase SQL Editor
-- ========================================

-- Adicionar campos de log na tabela guild_config
ALTER TABLE guild_config 
ADD COLUMN IF NOT EXISTS log_channel_id BIGINT,
ADD COLUMN IF NOT EXISTS log_events TEXT[];

-- Adicionar campo ticket_allowed_products (se não existir)
ALTER TABLE guild_config
ADD COLUMN IF NOT EXISTS ticket_allowed_products INTEGER[];

-- Comentários
COMMENT ON COLUMN guild_config.log_channel_id IS 'ID do canal Discord para logs';
COMMENT ON COLUMN guild_config.log_events IS 'Array de event_ids para logar';
COMMENT ON COLUMN guild_config.ticket_allowed_products IS 'IDs de produtos permitidos em tickets';

-- Verificar se funcionou
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'guild_config' 
  AND column_name IN ('log_channel_id', 'log_events', 'ticket_allowed_products')
ORDER BY column_name;

-- Mensagem de sucesso
SELECT '✅ Campos de log adicionados com sucesso!' as status;

