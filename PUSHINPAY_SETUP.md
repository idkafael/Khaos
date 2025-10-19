# 🔧 Configuração PushinPay

## 📋 Sobre a PushinPay

A PushinPay é uma gateway de pagamento brasileira especializada em Pix que oferece:
- ✅ Geração de QR Code Pix
- ✅ Código "copia e cola" 
- ✅ Webhooks para notificações
- ✅ API simples e documentada
- ✅ Ambiente sandbox para testes

## 🚀 Como Configurar

### 1. Criar Conta na PushinPay

1. Acesse [pushinpay.com.br](https://pushinpay.com.br)
2. Clique em "Criar Conta"
3. Preencha os dados da empresa
4. Confirme o email

### 2. Obter Credenciais

1. Faça login no painel
2. Vá para **Configurações > API**
3. Copie sua **API Key**
4. (Opcional) Configure **Webhook Secret**

### 3. Configurar Webhook (Opcional)

Para receber notificações automáticas de pagamento:

1. No painel PushinPay, vá para **Webhooks**
2. Adicione a URL: `https://seu-dominio.com/webhook/pushinpay`
3. Selecione os eventos: `payment.paid`, `payment.failed`
4. Copie o **Webhook Secret**

### 4. Configurar no Bot

Edite o arquivo `.env`:

```env
# PushinPay
PUSHINPAY_API_KEY=sua_api_key_aqui
PUSHINPAY_WEBHOOK_SECRET=seu_webhook_secret_aqui
WEBHOOK_BASE_URL=https://seu-dominio.com
```

## 🧪 Ambiente de Teste

A PushinPay oferece ambiente sandbox:

1. No painel, ative **Modo Sandbox**
2. Use valores baixos para teste (ex: R$ 0,01)
3. QR Codes de teste funcionam normalmente

## 📊 Status de Pagamento

A PushinPay retorna os seguintes status:

| Status PushinPay | Status Bot | Descrição |
|------------------|------------|-----------|
| `created` | `pending` | Aguardando pagamento |
| `paid` | `approved` | Pagamento confirmado |
| `expired` | `failed` | Pagamento expirado |

**Nota**: PushinPay não oferece cancelamento via API. Os pagamentos expiram automaticamente.

## 🔄 Webhook (Opcional)

Se configurar webhook, o bot receberá notificações automáticas:

```python
# Exemplo de webhook handler
@app.route('/webhook/pushinpay', methods=['POST'])
def pushinpay_webhook():
    data = request.json
    
    if data['event'] == 'payment.paid':
        # Atualizar status no banco
        # Notificar usuário no Discord
        pass
```

## 💰 Valores e Taxas

- **Valores**: PushinPay usa centavos (R$ 10,00 = 1000 centavos)
- **Valor mínimo**: 50 centavos (R$ 0,50)
- **Taxas**: Consulte o site para valores atualizados
- **Limites**: Verifique limites na documentação

## 🔗 Endpoints da API

### Produção:
- **Base URL**: `https://api.pushinpay.com.br`
- **Criar PIX**: `POST /api/pix/cashIn`
- **Consultar PIX**: `GET /api/transactions/{ID}`

### Sandbox:
- **Base URL**: `https://api-sandbox.pushinpay.com.br`
- **Criar PIX**: `POST /api/pix/cashIn`
- **Consultar PIX**: `GET /api/transactions/{ID}`

## 🆘 Suporte

- **Documentação**: [doc.pushinpay.com.br](https://doc.pushinpay.com.br)
- **Suporte**: Através do painel PushinPay
- **Status**: [status.pushinpay.com.br](https://status.pushinpay.com.br)

## ✅ Testando a Integração

1. Configure as credenciais
2. Execute o bot: `python bot.py`
3. Use o comando: `!start`
4. Escolha um produto: `!buy Camiseta Estilo 2025`
5. Digite seu email
6. Teste o pagamento com valor baixo

---

**🎉 PushinPay configurada com sucesso!**
