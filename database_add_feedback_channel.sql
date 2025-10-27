-- Adicionar coluna feedback_channel_id na tabela guild_config
ALTER TABLE guild_config
ADD COLUMN IF NOT EXISTS feedback_channel_id BIGINT;

-- Adicionar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_guild_config_feedback_channel 
ON guild_config(feedback_channel_id);

