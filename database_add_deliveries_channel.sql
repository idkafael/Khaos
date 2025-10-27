-- Adicionar coluna deliveries_channel_id na tabela guild_config
ALTER TABLE guild_config
ADD COLUMN IF NOT EXISTS deliveries_channel_id BIGINT;

-- Adicionar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_guild_config_deliveries_channel 
ON guild_config(deliveries_channel_id);

-- Comentário para documentar a coluna
COMMENT ON COLUMN guild_config.deliveries_channel_id IS 'ID do canal para mostrar entregas/publicar compras confirmadas';

