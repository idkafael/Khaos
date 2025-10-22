# ✅ Checklist Final - O que falta fazer

## 🔧 1. Alterar o Prefixo do Bot

No seu arquivo `.env`, altere esta linha:

**ANTES:**
```env
BOT_PREFIX=!
```

**DEPOIS:**
```env
BOT_PREFIX=?
```

Agora seus comandos serão: `?start`, `?products`, `?buy`, etc.

---

## 🗄️ 2. Configurar o Banco de Dados no Supabase

### ⚠️ ISSO É ESSENCIAL - SEM ISSO O BOT NÃO FUNCIONA!

Você precisa executar o SQL no Supabase para criar as tabelas:

#### **Passo a Passo:**

1. **Acesse seu projeto no Supabase:**
   - Vá em: https://supabase.com/dashboard
   - Entre no seu projeto (sxsaxcqliuiolktypwkf)

2. **Abra o SQL Editor:**
   - Menu lateral → **SQL Editor**
   - Clique em **"New query"**

3. **Execute PRIMEIRO este SQL (Tabelas Principais):**

```sql
-- ================================================
-- TABELAS PRINCIPAIS
-- ================================================

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    vip_config JSONB DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de transações
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id INTEGER REFERENCES products(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    email VARCHAR(255),
    payment_id VARCHAR(255),
    pix_code TEXT,
    qr_code TEXT,
    coupon_id INTEGER,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
```

4. **Execute DEPOIS este SQL (Sistema de Cupons):**

```sql
-- ================================================
-- SISTEMA DE CUPONS
-- ================================================

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

CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(code);
CREATE INDEX IF NOT EXISTS idx_coupons_active ON coupons(active);

CREATE TABLE IF NOT EXISTS coupon_usage (
    id SERIAL PRIMARY KEY,
    coupon_id INTEGER REFERENCES coupons(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    discount_amount DECIMAL(10,2),
    used_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coupon_usage_user ON coupon_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_coupon ON coupon_usage(coupon_id);
CREATE INDEX IF NOT EXISTS idx_coupon_usage_transaction ON coupon_usage(transaction_id);

-- Inserir cupons de exemplo
INSERT INTO coupons (code, discount_percent, max_uses, one_per_user, active, created_by) VALUES
('PRIMEIRACOMPRA', 15, NULL, true, true, 0),
('CAOS', 30, NULL, false, true, 0),
('VIP10', 10, 100, false, true, 0)
ON CONFLICT (code) DO NOTHING;
```

5. **Execute POR ÚLTIMO este SQL (Sistema VIP):**

```sql
-- ================================================
-- SISTEMA VIP
-- ================================================

CREATE TABLE IF NOT EXISTS vip_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    duration_days INTEGER NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled')),
    transaction_id INTEGER NULL REFERENCES transactions(id) ON DELETE SET NULL,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vip_user_id ON vip_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_vip_guild_id ON vip_subscriptions(guild_id);
CREATE INDEX IF NOT EXISTS idx_vip_status ON vip_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_vip_expires_at ON vip_subscriptions(expires_at);
CREATE INDEX IF NOT EXISTS idx_vip_user_status ON vip_subscriptions(user_id, status);
```

6. **Execute este SQL (Funções e Triggers):**

```sql
-- ================================================
-- FUNÇÕES E TRIGGERS
-- ================================================

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_products_updated_at 
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at 
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coupons_updated_at 
BEFORE UPDATE ON coupons
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_vip_updated_at
BEFORE UPDATE ON vip_subscriptions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Função para incrementar uso de cupom
CREATE OR REPLACE FUNCTION increment_coupon_uses(coupon_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE coupons 
    SET uses_count = uses_count + 1,
        updated_at = NOW()
    WHERE id = coupon_id;
END;
$$ LANGUAGE plpgsql;
```

7. **IMPORTANTE - Desabilitar RLS (Row Level Security):**

```sql
-- ================================================
-- DESABILITAR RLS (IMPORTANTE!)
-- ================================================

ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE coupons DISABLE ROW LEVEL SECURITY;
ALTER TABLE coupon_usage DISABLE ROW LEVEL SECURITY;
ALTER TABLE vip_subscriptions DISABLE ROW LEVEL SECURITY;
```

8. **Verificar se deu certo:**

```sql
-- Ver todas as tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Deve mostrar: coupons, coupon_usage, products, transactions, vip_subscriptions
```

---

## 📦 3. Instalar Dependências (se ainda não fez)

No terminal, na pasta do projeto:

```bash
pip install -r requirements.txt
```

---

## 🚀 4. Testar o Bot

```bash
python bot.py
```

Se aparecer algo como:
```
Bot conectado como: SeuBot#1234
```

**✅ ESTÁ FUNCIONANDO!**

---

## 🎮 5. Testar Comandos no Discord

Com o bot online no servidor:

```
?start           - Abrir ticket de compra
?products        - Ver produtos disponíveis
?buy VIP Mensal  - Comprar produto
?cupom CAOS      - Usar cupom
?vip             - Ver status VIP
```

---

## 📋 Checklist Resumido

- [ ] Alterar `BOT_PREFIX=?` no arquivo `.env`
- [ ] Executar SQL 1 (Tabelas Principais) no Supabase
- [ ] Executar SQL 2 (Sistema de Cupons) no Supabase
- [ ] Executar SQL 3 (Sistema VIP) no Supabase
- [ ] Executar SQL 4 (Funções e Triggers) no Supabase
- [ ] Executar SQL 5 (Desabilitar RLS) no Supabase
- [ ] Verificar se tabelas foram criadas
- [ ] Executar `pip install -r requirements.txt`
- [ ] Executar `python bot.py`
- [ ] Testar comandos no Discord

---

## ⚠️ O QUE PODE DAR ERRADO

### Erro: "relation products does not exist"
**Solução:** Você não executou o SQL no Supabase. Volte e execute.

### Erro: "permission denied for table products"
**Solução:** Execute o SQL que desabilita o RLS.

### Bot não responde comandos
**Solução:** Verifique se o prefixo está correto no `.env` e reinicie o bot.

---

**🎉 Depois disso, seu bot estará 100% funcional!**

