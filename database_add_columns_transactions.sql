-- =====================================================
-- ADICIONAR COLUNAS NECESSÁRIAS NA TABELA TRANSACTIONS
-- Execute este SQL ANTES dos testes de carteira
-- =====================================================

-- 1) Adicionar coluna guild_id (obrigatório para multi-servidor)
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS guild_id BIGINT;

-- 2) Adicionar coluna gateway_used (qual gateway processou o pagamento)
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS gateway_used VARCHAR(50);

-- 3) Adicionar coluna platform_fee (taxa da plataforma cobrada)
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS platform_fee DECIMAL(10,2) DEFAULT 0.00;

-- 4) Criar índice para melhorar performance de buscas por servidor
CREATE INDEX IF NOT EXISTS idx_transactions_guild_id ON transactions(guild_id);

-- 5) Criar índice para filtrar por gateway
CREATE INDEX IF NOT EXISTS idx_transactions_gateway ON transactions(gateway_used);

-- ✅ Pronto! Agora a tabela está preparada para o sistema Micro SaaS

