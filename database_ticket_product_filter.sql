-- ========================================
-- ADICIONAR FILTRO DE PRODUTOS NOS TICKETS
-- ========================================
-- Execute este SQL no Supabase para adicionar suporte a filtro de produtos

-- Adicionar campo para armazenar IDs dos produtos permitidos no ticket
ALTER TABLE guild_config ADD COLUMN IF NOT EXISTS ticket_allowed_products INTEGER[];

-- Criar índice para melhorar performance
CREATE INDEX IF NOT EXISTS idx_guild_config_ticket_products ON guild_config USING GIN (ticket_allowed_products);

-- ========================================
-- VERIFICAÇÃO
-- ========================================

SELECT 'Campo ticket_allowed_products adicionado!' as status
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'guild_config' 
    AND column_name = 'ticket_allowed_products'
);

-- ========================================
-- COMO USAR
-- ========================================

-- Exemplo 1: Permitir apenas produtos 1, 2, 3 no ticket
-- UPDATE guild_config 
-- SET ticket_allowed_products = ARRAY[1, 2, 3] 
-- WHERE guild_id = SEU_GUILD_ID;

-- Exemplo 2: Permitir todos os produtos (remover filtro)
-- UPDATE guild_config 
-- SET ticket_allowed_products = NULL 
-- WHERE guild_id = SEU_GUILD_ID;

-- Exemplo 3: Ver configuração atual
-- SELECT guild_id, ticket_allowed_products 
-- FROM guild_config;

-- ========================================
-- NOTAS
-- ========================================
-- • NULL = Todos produtos disponíveis
-- • ARRAY[1,2,3] = Apenas produtos com IDs 1, 2 e 3
-- • O bot aplica o filtro automaticamente ao usar /setup_ticket


