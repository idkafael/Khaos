-- ========================================
-- ADICIONAR GUILD_ID NA TABELA TRANSACTIONS
-- ========================================
-- Execute este SQL no Supabase SQL Editor
-- ========================================

-- Adicionar coluna guild_id na tabela transactions
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS guild_id BIGINT;

-- Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_transactions_guild 
ON transactions(guild_id);

-- Criar índice composto para queries comuns
CREATE INDEX IF NOT EXISTS idx_transactions_guild_status 
ON transactions(guild_id, status);

-- Comentário
COMMENT ON COLUMN transactions.guild_id IS 'ID do servidor Discord onde a transação foi criada';

-- Verificar se funcionou
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'transactions' 
  AND column_name = 'guild_id';

-- Mensagem de sucesso
SELECT '✅ Campo guild_id adicionado na tabela transactions!' as status;

-- ========================================
-- OPCIONAL: Atualizar transações existentes
-- ========================================
-- Se você tiver transações antigas sem guild_id,
-- você pode atualizar com um ID padrão:
-- 
-- UPDATE transactions 
-- SET guild_id = SEU_SERVER_ID_AQUI 
-- WHERE guild_id IS NULL;
-- ========================================

