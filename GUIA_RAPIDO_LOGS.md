# 🚀 Guia Rápido - Sistema de Logs

## ❌ Erro: "Erro ao salvar configuração de logs"

### 🔧 Solução (2 minutos)

#### Passo 1: Execute o SQL no Supabase
1. Acesse: https://supabase.com
2. Vá em **SQL Editor** → **New query**
3. Abra o arquivo `database_add_log_fields.sql`
4. **Copie todo conteúdo** e cole no SQL Editor
5. Clique em **RUN** ▶️

#### Passo 2: Teste no Discord
```
/setlog #canal-logs
```

### ✅ Pronto! Agora deve funcionar!

---

## 📊 Eventos Disponíveis

### 💰 Vendas (Mais Usado)
- ✅ `payment_confirmed` - Pagamentos confirmados
- 📦 `product_delivered` - Produtos entregues
- 💳 `payment_generated` - Pagamentos gerados

### 🎫 Tickets
- 🎫 `ticket_created` - Tickets de compra criados
- 🆘 `support_ticket_created` - Tickets de suporte criados
- 🔒 `ticket_closed` - Tickets fechados

### 🎁 Extras
- 🎟️ `coupon_used` - Cupons utilizados
- 👑 `vip_activated` - VIP ativado
- ⏰ `vip_expired` - VIP expirado
- 📦 `stock_added` - Estoque adicionado
- ➕ `product_created` - Produtos criados

---

## 🎯 Presets Recomendados

### 🔥 Apenas Vendas
```
Selecionar:
- payment_confirmed
- product_delivered
```

### 🎫 Apenas Tickets
```
Selecionar:
- ticket_created
- support_ticket_created
- ticket_closed
```

### 📊 Completo
```
Selecionar todos os eventos
```

---

## 💡 Dicas

1. **Múltipla Seleção** - Você pode escolher quantos eventos quiser
2. **Presets** - Use os botões para configuração rápida
3. **Desabilitar** - Deixe vazio ou clique "Desabilitar Logs"
4. **Reconfigurar** - Use `/setlog` novamente para mudar

---

## 🎨 Exemplo de Log

```
┌─────────────────────────────────────┐
│ ✅ Pagamento Confirmado             │
│ 💰 Pagamento via Pix confirmado!    │
│                                     │
│ 👤 João (123456789)                 │
│                                     │
│ 🛍️ Produto: VIP Gold - 30 Dias      │
│ 💵 Valor: R$ 49.90                  │
│ 🆔 Transação: #42                   │
│                                     │
│ 24/10/2025 às 15:30                │
└─────────────────────────────────────┘
```

---

## 🚨 Troubleshooting

### Erro: "Erro ao salvar configuração de logs"
**Causa:** Campos não existem no Supabase  
**Solução:** Execute `database_add_log_fields.sql`

### Logs não aparecem
**Causa 1:** Eventos não selecionados  
**Solução:** Use `/setlog` e selecione eventos

**Causa 2:** Canal errado  
**Solução:** Verifique se o bot tem permissão para enviar mensagens

### Select menu não aparece
**Causa:** Bot não tem permissão  
**Solução:** Dê permissão de Administrator ao bot

---

**🎯 Sistema de Logs Personalizado v1.0**

