# 🔍 DEBUG: Erro ao gerar pagamento Mercado Pago

## ❌ Problema Identificado:

O bot está falhando ao criar pagamento Pix via Mercado Pago.

Mensagem de erro no Discord:
```
❌ Erro ao gerar pagamento Pix!
```

---

## 🔎 Possíveis Causas:

### 1️⃣ Credenciais não configuradas na Shard Cloud

**Verificar:**
- Vá na Shard Cloud → Settings → Environment Variables
- Confirme que existem:
  ```
  MERCADOPAGO_ACCESS_TOKEN = APP_USR-...
  MERCADOPAGO_PUBLIC_KEY = APP_USR-...
  ```

**Se não tiver:**
- Adicione as variáveis
- **Salve** e **Reinicie** o bot

---

### 2️⃣ Credenciais inválidas

**Teste:**
1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Vá em "Credenciais" → "Produção"
3. **Copie novamente** as credenciais
4. **Substitua** na Shard Cloud
5. Reinicie o bot

---

### 3️⃣ Falta WEBHOOK_URL

**Adicionar na Shard Cloud:**
```
WEBHOOK_URL = https://seu-bot.shardcloud.dev
```

(Substitua pelo URL real do seu bot na Shard Cloud)

---

### 4️⃣ Erro na API do Mercado Pago

**Verificar logs:**
1. Shard Cloud → Logs
2. Procure por:
   - `❌ Erro ao criar pagamento`
   - `Mercado Pago não configurado`
   - Status code diferente de 201

---

## 🧪 Teste Local (RECOMENDADO):

Execute este script localmente para ver o erro real:

```bash
python test_mercadopago.py
```

**Resultado esperado:**
```
✅ ACCESS_TOKEN encontrado: APP_USR-...
✅ PUBLIC_KEY encontrado: APP_USR-...
✅ SDK inicializado com sucesso!
✅ Pagamento criado com sucesso!
   ID: 123456789
   QR Code base64: Presente
   Pix Copia e Cola: Presente
```

**Se der erro:**
- Me envie a mensagem completa do erro
- Vou corrigir o código

---

## 🛠️ Correção Rápida:

Se você já tem as credenciais na Shard Cloud mas ainda não funciona:

### Opção A: Adicionar mais logs

Vou adicionar logs detalhados no código para ver exatamente onde está falhando.

### Opção B: Testar credenciais

Execute o `test_mercadopago.py` localmente com suas credenciais reais.

---

## 📞 Me envie:

Para eu te ajudar melhor, me envie:

1. ✅ **Print das variáveis de ambiente** da Shard Cloud (Settings → Environment Variables)
   - Pode cobrir parte das credenciais, só quero ver se estão lá

2. ✅ **Logs da Shard Cloud** quando você tenta comprar
   - Procure por linhas que começam com:
     - `💳 Iniciando pagamento`
     - `❌ Erro`
     - `Mercado Pago`

3. ✅ **Resultado do teste local** (se executar `test_mercadopago.py`)

---

## 🎯 Próximos Passos:

Assim que eu souber qual é o erro exato, vou:

1. ✅ Corrigir o código
2. ✅ Fazer commit
3. ✅ Push para deploy automático
4. ✅ Testar novamente

**Aguardo o feedback!** 🚀

