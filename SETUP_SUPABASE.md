# 🗄️ Configuração do Supabase - Passo a Passo

## 📋 O que você precisa fazer no Supabase

### 1️⃣ Criar Conta e Projeto no Supabase

1. Acesse: https://supabase.com
2. Clique em **"Start your project"** ou **"Sign in"**
3. Crie uma conta (pode usar GitHub)
4. Clique em **"New Project"**
5. Preencha:
   - **Name**: CaosBot (ou qualquer nome)
   - **Database Password**: Escolha uma senha forte (ANOTE!)
   - **Region**: South America (São Paulo) - para menor latência
   - **Pricing Plan**: Free (suficiente para começar)
6. Clique em **"Create new project"** e aguarde ~2 minutos

---

### 2️⃣ Copiar Credenciais do Supabase

Depois que o projeto for criado:

1. No painel do Supabase, vá em **Settings** (engrenagem no menu lateral)
2. Clique em **API**
3. Copie as seguintes informações:

```
📋 ANOTE ESTAS INFORMAÇÕES:

URL: https://xxxxxxxxxx.supabase.co
anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3️⃣ Criar as Tabelas no Banco de Dados

Agora vamos criar todas as tabelas necessárias:

#### **PASSO 1: Abrir SQL Editor**
1. No menu lateral do Supabase, clique em **SQL Editor**
2. Clique em **"New query"**

#### **PASSO 2: Copiar e Executar o SQL Completo**

Cole este SQL completo e clique em **"Run"** (ou F5):

```sql
-- ================================================
-- TABELA DE PRODUTOS
-- ================================================
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

-- ================================================
-- TABELA DE TRANSAÇÕES
-- ================================================
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

-- ================================================
-- TABELA DE CUPONS
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

-- ================================================
-- TABELA DE USO DE CUPONS
-- ================================================
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

-- ================================================
-- TABELA DE ASSINATURAS VIP
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

-- ================================================
-- FUNÇÕES E TRIGGERS
-- ================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para produtos
CREATE TRIGGER update_products_updated_at 
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para transações
CREATE TRIGGER update_transactions_updated_at 
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para cupons
CREATE TRIGGER update_coupons_updated_at 
BEFORE UPDATE ON coupons
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para VIP
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

-- ================================================
-- DADOS DE EXEMPLO (Opcional)
-- ================================================

-- Inserir cupons de exemplo
INSERT INTO coupons (code, discount_percent, max_uses, one_per_user, active, created_by) VALUES
('PRIMEIRACOMPRA', 15, NULL, true, true, 0),
('CAOS', 30, NULL, false, true, 0),
('VIP10', 10, 100, false, true, 0)
ON CONFLICT (code) DO NOTHING;

-- Inserir produto de exemplo
INSERT INTO products (name, description, price, category) VALUES
('VIP Mensal', 'Acesso VIP por 30 dias com benefícios exclusivos', 19.90, 'vip'),
('VIP Vitalício', 'Acesso VIP permanente', 99.90, 'vip'),
('Produto Teste', 'Produto de teste para validação', 5.00, 'teste')
ON CONFLICT DO NOTHING;
```

#### **PASSO 3: Verificar se funcionou**

Execute esta query para ver se as tabelas foram criadas:

```sql
-- Ver todas as tabelas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Ver cupons criados
SELECT * FROM coupons;

-- Ver produtos criados
SELECT * FROM products;
```

Se aparecer as tabelas `coupons`, `coupon_usage`, `products`, `transactions` e `vip_subscriptions`, está tudo certo! ✅

---

### 4️⃣ Configurar Variáveis de Ambiente

Agora crie ou edite o arquivo `.env` na raiz do projeto:

```env
# Discord
DISCORD_TOKEN=seu_token_do_discord
DISCORD_APPLICATION_ID=seu_application_id

# Supabase (cole as credenciais que você copiou)
SUPABASE_URL=https://xxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# PushinPay
PUSHINPAY_API_KEY=sua_chave_pushinpay
PUSHINPAY_SANDBOX=true

# Opcional
BOT_PREFIX=!
```

---

### 5️⃣ Testar a Conexão

Execute o bot para testar:

```bash
python bot.py
```

Se aparecer mensagens de erro relacionadas ao Supabase, verifique:
1. ✅ SUPABASE_URL está correto
2. ✅ SUPABASE_KEY está correto (deve ser a chave **anon/public**)
3. ✅ As tabelas foram criadas corretamente

---

## 🔧 Configurações Adicionais (Opcional)

### Habilitar Row Level Security (RLS)

Por padrão, o Supabase cria as tabelas sem RLS. Como você está usando a chave `anon`, é importante configurar:

**Opção 1: Desabilitar RLS (mais fácil para começar)**
```sql
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE coupons DISABLE ROW LEVEL SECURITY;
ALTER TABLE coupon_usage DISABLE ROW LEVEL SECURITY;
ALTER TABLE vip_subscriptions DISABLE ROW LEVEL SECURITY;
```

**Opção 2: Criar políticas (mais seguro)**
```sql
-- Habilitar RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE coupons ENABLE ROW LEVEL SECURITY;
ALTER TABLE coupon_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE vip_subscriptions ENABLE ROW LEVEL SECURITY;

-- Criar política que permite tudo com a chave anon
CREATE POLICY "Enable all for anon" ON products FOR ALL USING (true);
CREATE POLICY "Enable all for anon" ON transactions FOR ALL USING (true);
CREATE POLICY "Enable all for anon" ON coupons FOR ALL USING (true);
CREATE POLICY "Enable all for anon" ON coupon_usage FOR ALL USING (true);
CREATE POLICY "Enable all for anon" ON vip_subscriptions FOR ALL USING (true);
```

---

## ✅ Checklist Final

- [ ] Projeto criado no Supabase
- [ ] Credenciais copiadas (URL + Key)
- [ ] SQL executado com sucesso
- [ ] Tabelas verificadas (5 tabelas criadas)
- [ ] Arquivo `.env` configurado
- [ ] RLS configurado (desabilitado ou com políticas)
- [ ] Bot testado e conectando no Supabase

---

## 🆘 Problemas Comuns

### "relation does not exist"
- As tabelas não foram criadas. Execute o SQL novamente.

### "permission denied"
- RLS está ativo. Execute o SQL de desabilitar RLS ou criar políticas.

### "connect ECONNREFUSED"
- SUPABASE_URL está errado. Verifique no painel do Supabase.

### "invalid API key"
- SUPABASE_KEY está errado. Use a chave **anon/public**, não a service_role.

---

**🎉 Pronto! Seu Supabase está configurado e funcional!**

