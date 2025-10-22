-- ========================================
-- MIGRAÇÃO PARA SISTEMA MULTI-SERVIDOR V2
-- ========================================
-- Esta versão pode ser executada múltiplas vezes sem erros

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

-- Deletar trigger se existir e criar novamente
DROP TRIGGER IF EXISTS trigger_guild_config_updated_at ON guild_config;

CREATE TRIGGER trigger_guild_config_updated_at
BEFORE UPDATE ON guild_config
FOR EACH ROW
EXECUTE FUNCTION update_guild_config_updated_at();

-- ========================================
-- PRONTO! Agora execute os passos abaixo:
-- ========================================

-- PASSO 2: MIGRAR DADOS EXISTENTES
-- SUBSTITUA 1300173398982393937 pelo ID do seu servidor Discord principal

-- Descomentar as 3 linhas abaixo e executar:
-- UPDATE products SET guild_id = 1300173398982393937 WHERE guild_id IS NULL;
-- UPDATE coupons SET guild_id = 1300173398982393937 WHERE guild_id IS NULL;
-- UPDATE product_inventory SET guild_id = 1300173398982393937 WHERE guild_id IS NULL;

-- PASSO 3: TORNAR OBRIGATÓRIO (só após migrar dados)
-- Descomentar as 3 linhas abaixo e executar:
-- ALTER TABLE products ALTER COLUMN guild_id SET NOT NULL;
-- ALTER TABLE coupons ALTER COLUMN guild_id SET NOT NULL;
-- ALTER TABLE product_inventory ALTER COLUMN guild_id SET NOT NULL;

-- ========================================
-- VERIFICAÇÃO
-- ========================================

SELECT 'Tabela guild_config criada!' as status
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'guild_config'
);

SELECT 'Coluna guild_id adicionada em products!' as status
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'products' 
    AND column_name = 'guild_id'
);

SELECT 'Coluna guild_id adicionada em coupons!' as status
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'coupons' 
    AND column_name = 'guild_id'
);

SELECT 'Coluna guild_id adicionada em product_inventory!' as status
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'product_inventory' 
    AND column_name = 'guild_id'
);

