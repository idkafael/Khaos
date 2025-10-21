-- ========================================
-- SISTEMA DE CUPONS - SQL SETUP
-- ========================================
-- Execute este SQL no Supabase para criar as tabelas e funções necessárias

-- 1. Criar tabela de cupons
CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent DECIMAL(5,2) NOT NULL CHECK (discount_percent >= 0 AND discount_percent <= 100),
    max_uses INTEGER DEFAULT NULL,
    uses_count INTEGER DEFAULT 0,
    one_per_user BOOLEAN DEFAULT false,
    split_enabled BOOLEAN DEFAULT false,
    split_recipient_id VARCHAR(255),
    split_percent DECIMAL(5,2),
    expires_at TIMESTAMP,
    active BOOLEAN DEFAULT true,
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_active ON coupons(active);

-- 3. Criar tabela de uso de cupons
CREATE TABLE IF NOT EXISTS coupon_usage (
    id SERIAL PRIMARY KEY,
    coupon_id INTEGER REFERENCES coupons(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    discount_amount DECIMAL(10,2),
    used_at TIMESTAMP DEFAULT NOW()
);

-- 4. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_coupon_usage_user ON coupon_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_coupon ON coupon_usage(coupon_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_transaction ON coupon_usage(transaction_id);

-- 5. Atualizar tabela transactions para suportar cupons
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS coupon_id INTEGER REFERENCES coupons(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS final_amount DECIMAL(10,2);

-- 6. Criar função para incrementar contador de usos do cupom
CREATE OR REPLACE FUNCTION increment_coupon_uses(coupon_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE coupons 
    SET uses_count = uses_count + 1,
        updated_at = NOW()
    WHERE id = coupon_id;
END;
$$ LANGUAGE plpgsql;

-- 7. Criar trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_coupons_updated_at 
BEFORE UPDATE ON coupons
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 8. Inserir cupons de exemplo (opcional)
INSERT INTO coupons (code, discount_percent, max_uses, one_per_user, active, created_by) VALUES
('PRIMEIRACOMPRA', 15, NULL, true, true, 0),
('CAOS', 30, NULL, false, true, 0),
('VIP10', 10, 100, false, true, 0)
ON CONFLICT (code) DO NOTHING;

-- ========================================
-- VERIFICAÇÕES
-- ========================================

-- Verificar se as tabelas foram criadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('coupons', 'coupon_usage');

-- Verificar cupons de exemplo
SELECT * FROM coupons;

