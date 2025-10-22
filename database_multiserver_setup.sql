-- ========================================
-- MIGRAÇÃO PARA SISTEMA MULTI-SERVIDOR
-- ========================================
-- Execute este SQL no Supabase para adicionar suporte multi-servidor

-- 1. Criar tabela de configuração por servidor
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id BIGINT PRIMARY KEY,
    guild_name VARCHAR(255),
    pushinpay_api_key VARCHAR(255),
    pushinpay_split_percent DECIMAL(5,2) DEFAULT 0,
    pushinpay_split_recipient_id VARCHAR(255),
    admin_role_ids BIGINT[],
    ticket_category_id BIGINT,
    ticket_logs_channel_id BIGINT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Adicionar guild_id nas tabelas existentes
ALTER TABLE products ADD COLUMN IF NOT EXISTS guild_id BIGINT;
ALTER TABLE coupons ADD COLUMN IF NOT EXISTS guild_id BIGINT;
ALTER TABLE product_inventory ADD COLUMN IF NOT EXISTS guild_id BIGINT;

-- 3. Criar índices compostos para performance
CREATE INDEX IF NOT EXISTS idx_products_guild ON products(guild_id);
CREATE INDEX IF NOT EXISTS idx_products_guild_category ON products(guild_id, category);
CREATE INDEX IF NOT EXISTS idx_products_guild_active ON products(guild_id) WHERE category IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_coupons_guild ON coupons(guild_id);
CREATE INDEX IF NOT EXISTS idx_coupons_guild_active ON coupons(guild_id, active);

CREATE INDEX IF NOT EXISTS idx_inventory_guild ON product_inventory(guild_id);
CREATE INDEX IF NOT EXISTS idx_inventory_guild_status ON product_inventory(guild_id, status);

-- 4. Trigger para atualizar updated_at na guild_config
CREATE OR REPLACE FUNCTION update_guild_config_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_guild_config_updated_at
BEFORE UPDATE ON guild_config
FOR EACH ROW
EXECUTE FUNCTION update_guild_config_updated_at();

-- ========================================
-- MIGRAÇÃO DE DADOS EXISTENTES
-- ========================================

-- IMPORTANTE: Substitua SEU_GUILD_ID pelo ID do seu servidor principal
-- Exemplo: UPDATE products SET guild_id = 1234567890123456789 WHERE guild_id IS NULL;

-- Descomentar e executar após substituir o ID:
-- UPDATE products SET guild_id = SEU_GUILD_ID WHERE guild_id IS NULL;
-- UPDATE coupons SET guild_id = SEU_GUILD_ID WHERE guild_id IS NULL;
-- UPDATE product_inventory SET guild_id = SEU_GUILD_ID WHERE guild_id IS NULL;

-- ========================================
-- VERIFICAÇÃO
-- ========================================

-- Ver tabelas criadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'guild_config';

-- Ver colunas adicionadas
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'products' 
AND column_name = 'guild_id';

COMMENT ON TABLE guild_config IS 'Configurações específicas de cada servidor Discord';
COMMENT ON COLUMN guild_config.guild_id IS 'ID do servidor Discord';
COMMENT ON COLUMN guild_config.pushinpay_api_key IS 'API Key PushinPay específica do servidor (opcional)';
COMMENT ON COLUMN guild_config.pushinpay_split_percent IS 'Porcentagem de split para o dono do bot (0-100)';
COMMENT ON COLUMN guild_config.admin_role_ids IS 'IDs das roles que podem gerenciar produtos';

