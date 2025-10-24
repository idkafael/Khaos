# 🚀 Setup Rápido - Micro SaaS

## ⚡ Checklist de Instalação (15 minutos)

### ✅ **1. Configurar Mercado Pago** (5 min)

**1.1 - Criar Conta**
- Acesse: https://www.mercadopago.com.br
- Cadastre-se com CPF (pessoa física)
- Verifique conta (envie documentos)

**1.2 - Criar Aplicação**
1. Entre em: https://www.mercadopago.com.br/developers
2. Clique em "Suas integrações"
3. "Criar aplicação"
4. Preencha:
   - **Nome:** CaosBot
   - **Produto:** Checkout Transparente
   - **Qual produto você está integrando?** Pagamentos (Payments API)
5. Salvar

**1.3 - Copiar Credenciais**
- Vá em "Credenciais de produção"
- Copie:
  - `Access Token` (começa com APP_USR-)
  - `Public Key` (começa com APP_USR-)

---

### ✅ **2. Configurar Banco de Dados** (3 min)

**2.1 - Executar SQL**
1. Abra Supabase: https://supabase.com/dashboard
2. Vá em: **SQL Editor** → **New query**
3. Cole TODO o conteúdo de `database_saas_setup.sql`
4. Clique em **RUN** (executar)
5. Aguarde ~10 segundos

**2.2 - Verificar**
Execute este SQL para confirmar:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('guild_wallets', 'wallet_transactions', 'withdrawal_requests', 'platform_fees');
```
Deve retornar 4 tabelas ✅

---

### ✅ **3. Atualizar .env** (2 min)

Edite seu arquivo `.env` e adicione:

```env
# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=APP_USR-cole-seu-token-aqui
MERCADOPAGO_PUBLIC_KEY=APP_USR-cole-sua-key-aqui
MERCADOPAGO_WEBHOOK_SECRET=  # Deixe vazio por enquanto
```

**⚠️ IMPORTANTE:** Use credenciais de **PRODUÇÃO**, não de teste!

---

### ✅ **4. Instalar Dependências** (2 min)

```bash
pip install -r requirements.txt
```

Aguarde instalação do `mercadopago` e `fastapi`.

---

### ✅ **5. Reiniciar Bot** (1 min)

```bash
# Parar bot atual (Ctrl+C)
# Iniciar novamente
python bot.py
```

**Procure no console:**
```
✅ Mercado Pago SDK inicializado
🌐 Webhook server iniciado na porta 8080
```

---

### ✅ **6. Configurar Webhook (Apenas em Produção)** (2 min)

**⚠️ FAÇA ISSO APENAS APÓS DEPLOY NA SHARD CLOUD!**

1. Acesse painel Mercado Pago: https://www.mercadopago.com.br/developers
2. Vá em sua aplicação
3. Clique em "Webhooks"
4. "Criar webhook"
5. Preencha:
   - **URL:** `https://seu-bot.shardcloud.app/webhook/mercadopago`
   - **Eventos:** Selecione apenas `payment`
6. Salvar

---

## 🧪 **Testar Localmente (Opcional)**

### **Teste 1: Ver se comandos apareceram**
No Discord, digite `/saldo` e veja se o comando existe.

### **Teste 2: Simular venda**
```python
# Execute no Python (fora do Discord)
from models.wallet_model import WalletModel
import asyncio

async def test():
    wallet = WalletModel()
    success = await wallet.credit_wallet(
        guild_id=123456789,  # ID do seu servidor
        amount=100.00,
        transaction_id=1,
        description="Teste"
    )
    print(f"Sucesso: {success}")

asyncio.run(test())
```

### **Teste 3: Ver saldo no Discord**
1. Digite `/saldo` no servidor
2. Deve aparecer R$ 99,20 disponível (R$ 100 - R$ 0,80 taxa)

---

## 📊 **Primeira Venda Real**

### **Passo a Passo:**

**1. Cliente cria ticket**
- Clica em "Criar Ticket de Compra"
- Escolhe produto

**2. Bot gera Pix**
- QR Code é enviado
- Pagamento vai para SUA CONTA Mercado Pago

**3. Cliente paga**
- Escaneia QR Code
- Paga

**4. Webhook notifica bot**
- Mercado Pago → Webhook → Bot
- Carteira creditada automaticamente
- Produto entregue

**5. Verificar**
```
/saldo → Deve mostrar saldo disponível
/historico_vendas → Deve listar a venda
```

---

## 💸 **Primeiro Saque**

### **Passo a Passo:**

**1. Configurar chave Pix (uma vez)**
```
/configurar_pix
  Chave: seu-cpf-aqui
  Tipo: CPF
```

**2. Solicitar saque**
```
/solicitar_saque
  Valor: 50.00
  (Deixe chave Pix vazia para usar padrão)
```

**3. Aguardar processamento**
- Bot processa automaticamente
- Pix enviado para sua chave
- Recebe DM de confirmação

**4. Verificar**
```
/historico_saques → Status: completed
```

---

## 🔧 **Troubleshooting**

### **Erro: "Mercado Pago não configurado"**
- Verifique se `MERCADOPAGO_ACCESS_TOKEN` está no `.env`
- Reinicie o bot

### **Erro: "Tabela guild_wallets não existe"**
- Execute `database_saas_setup.sql` no Supabase
- Verifique se executou sem erros

### **Webhook não funciona**
- URL deve ser PÚBLICA (não localhost)
- Use Shard Cloud ou Ngrok para testes
- Verificar logs do Mercado Pago

### **Saque não processou**
- Ver tabela `withdrawal_requests` → campo `status`
- Se `failed`, ver campo `error_message`
- Verificar saldo suficiente na conta Mercado Pago

---

## ✅ **Checklist Final**

Antes de colocar em produção, confirme:

- [ ] SQL executado no Supabase (4 tabelas criadas)
- [ ] Credenciais Mercado Pago no `.env`
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Bot reiniciado e sem erros
- [ ] Comando `/saldo` funciona
- [ ] Teste de venda simulada passou
- [ ] Webhook configurado (apenas após deploy)
- [ ] Primeira venda real testada
- [ ] Primeiro saque testado

---

## 🎯 **Está Pronto!**

Seu micro SaaS está funcionando! Agora é só:

1. **Divulgar** para donos de servidor Discord
2. **Receber** pagamentos na sua conta
3. **Processar** saques automaticamente
4. **Lucrar** com as taxas! 💰

---

## 📞 **Próximos Passos**

1. **Deploy na Shard Cloud** (recomendado)
2. **Configurar webhook** com URL pública
3. **Testar em produção** com venda real
4. **(Opcional) Criar painel web** para estatísticas

---

**Dúvidas? Problemas?**
- Veja `README_SAAS.md` para detalhes completos
- Confira logs do bot no console
- Verifique tabelas no Supabase

