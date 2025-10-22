-- ================================================
-- SISTEMA VIP - CONFIGURAÇÃO DO BANCO DE DADOS
-- ================================================

-- Criar tabela de assinaturas VIP
CREATE TABLE IF NOT EXISTS vip_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    duration_days INTEGER NULL, -- NULL = vitalício
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NULL, -- NULL = vitalício
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled')),
    transaction_id INTEGER NULL REFERENCES transactions(id) ON DELETE SET NULL,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_vip_user_id ON vip_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_vip_guild_id ON vip_subscriptions(guild_id);
CREATE INDEX IF NOT EXISTS idx_vip_status ON vip_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_vip_expires_at ON vip_subscriptions(expires_at);
CREATE INDEX IF NOT EXISTS idx_vip_user_status ON vip_subscriptions(user_id, status);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_vip_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_vip_updated_at
    BEFORE UPDATE ON vip_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_vip_updated_at();

-- Adicionar campo vip_config na tabela products (se não existir)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'vip_config'
    ) THEN
        ALTER TABLE products ADD COLUMN vip_config JSONB DEFAULT NULL;
    END IF;
END $$;

-- Comentários para documentação
COMMENT ON TABLE vip_subscriptions IS 'Armazena assinaturas VIP dos usuários no Discord';
COMMENT ON COLUMN vip_subscriptions.user_id IS 'ID do usuário no Discord';
COMMENT ON COLUMN vip_subscriptions.guild_id IS 'ID do servidor Discord';
COMMENT ON COLUMN vip_subscriptions.role_id IS 'ID da role VIP no Discord';
COMMENT ON COLUMN vip_subscriptions.duration_days IS 'Duração em dias (NULL = vitalício)';
COMMENT ON COLUMN vip_subscriptions.expires_at IS 'Data de expiração (NULL = vitalício)';
COMMENT ON COLUMN vip_subscriptions.status IS 'Status da assinatura: active, expired, cancelled';
COMMENT ON COLUMN products.vip_config IS 'Configuração VIP do produto (role_name, duration_days, benefits)';

-- Exemplos de consultas úteis:

-- Buscar assinaturas ativas de um usuário
-- SELECT * FROM vip_subscriptions WHERE user_id = ? AND status = 'active';

-- Buscar assinaturas que expiram nos próximos X dias
-- SELECT * FROM vip_subscriptions 
-- WHERE status = 'active' 
-- AND expires_at IS NOT NULL 
-- AND expires_at <= NOW() + INTERVAL '3 days';

-- Buscar assinaturas expiradas que precisam ser processadas
-- SELECT * FROM vip_subscriptions 
-- WHERE status = 'active' 
-- AND expires_at IS NOT NULL 
-- AND expires_at <= NOW();


