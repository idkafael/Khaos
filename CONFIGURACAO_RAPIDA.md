# 🚀 Configuração Rápida do Bot

## ✅ Suas Credenciais Configuradas

- **Discord**: Token + Application ID ✅
- **Supabase**: URL + API Key ✅  
- **PushinPay**: Token configurado ✅

## 🔧 Configuração Final

### 1. Crie o arquivo `.env`:
```env
# Discord
DISCORD_TOKEN=842c8e29352ebd03e85b29f8c1c4ed6ee2e981194ad0236c153e3bb234c3848f
DISCORD_APPLICATION_ID=784058182515425310

# Supabase
SUPABASE_URL=https://sxsaxcqliuiolktypwkf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4c2F4Y3FsaXVpb2xrdHlwd2tmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NTQwNDksImV4cCI6MjA3NjQzMDA0OX0.Qc-DINC-FC9oPbI4BBpxbtF9OmTMUN8ecC1gDSTatbY

# PushinPay
PUSHINPAY_API_KEY=50790|dakuggRtFoHjIZb2XpYYbDoa2exlT5NPspJayboI40bfb10f
PUSHINPAY_SANDBOX=true
```

### 2. Execute o SQL no Supabase:
Acesse [supabase.com/dashboard](https://supabase.com/dashboard) → SQL Editor e execute:

```sql
-- Tabela de produtos
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de transações
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id INTEGER REFERENCES products(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    email VARCHAR(255),
    payment_id VARCHAR(255),
    pix_code TEXT,
    qr_code TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
```

### 3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 4. Deploy do bot (escolha uma opção):

#### Opção A - Daki Hosting (Recomendado):
1. Acesse: https://dakihosting.com
2. Crie conta gratuita
3. Crie projeto Python
4. Upload dos arquivos
5. Configure variáveis de ambiente (veja `DEPLOY_GUIDE.md`)

#### Opção B - Teste local:
```bash
python bot.py
```

### 5. Convide o bot para seu servidor:
1. Acesse: https://discord.com/developers/applications/784058182515425310
2. Vá para **OAuth2 > URL Generator**
3. Selecione **bot** e **Send Messages**
4. Copie a URL e abra no navegador

## 🎮 Comandos para Testar

- `!start` - Criar ticket de compra
- `!products` - Ver produtos disponíveis  
- `!buy Camiseta Estilo 2025` - Comprar produto
- `!status` - Verificar status da compra

---

**🎉 Bot pronto para vender!**
