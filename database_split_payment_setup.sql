-- Sistema de Split de Pagamento - Mercado Pago
-- Execute este SQL no Supabase para adicionar suporte a split automático

-- 1. Adicionar campo Account ID na tabela guild_config
ALTER TABLE guild_config 
ADD COLUMN IF NOT EXISTS mercadopago_account_id VARCHAR(255);

-- 2. Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_guild_mp_account 
ON guild_config(mercadopago_account_id);

-- 3. Adicionar campos de split na tabela transactions
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS platform_fee DECIMAL(10,2) DEFAULT 0.80,
ADD COLUMN IF NOT EXISTS vendor_amount DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS vendor_account_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS split_applied BOOLEAN DEFAULT FALSE;

-- 4. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_transactions_split_applied 
ON transactions(split_applied);

CREATE INDEX IF NOT EXISTS idx_transactions_vendor_account 
ON transactions(vendor_account_id);

-- 5. Comentários para documentação
COMMENT ON COLUMN guild_config.mercadopago_account_id IS 'Account ID do Mercado Pago do servidor para split automático';
COMMENT ON COLUMN transactions.platform_fee IS 'Taxa da plataforma (R$ 0,80 fixo)';
COMMENT ON COLUMN transactions.vendor_amount IS 'Valor que vai para o vendedor (total - platform_fee)';
COMMENT ON COLUMN transactions.vendor_account_id IS 'Account ID do vendedor que recebe o pagamento';
COMMENT ON COLUMN transactions.split_applied IS 'Se o split foi aplicado automaticamente';
