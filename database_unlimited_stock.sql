-- ================================================
-- SISTEMA DE ESTOQUE ILIMITADO
-- ================================================
-- Adiciona suporte para produtos com estoque infinito
-- Perfeito para VIPs, roles e produtos digitais ilimitados

-- 1. Adicionar campo unlimited_stock na tabela products
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS unlimited_stock BOOLEAN DEFAULT false;

-- 2. Marcar produtos VIP existentes como estoque ilimitado
UPDATE products 
SET unlimited_stock = true 
WHERE category = 'vip';

-- 3. Criar índice para performance
CREATE INDEX IF NOT EXISTS idx_products_unlimited_stock 
ON products(unlimited_stock) 
WHERE unlimited_stock = true;

-- 4. Verificar produtos com estoque ilimitado
SELECT id, name, category, unlimited_stock 
FROM products 
WHERE unlimited_stock = true;

