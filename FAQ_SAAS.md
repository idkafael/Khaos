# ❓ FAQ - Micro SaaS Discord Bot

## 💰 **Perguntas sobre Monetização**

### **P: Como eu ganho dinheiro com isso?**
**R:** Você ganha de duas formas:
1. **R$ 0,80 por venda** - Taxa fixa em cada transação
2. **3% no saque** - Quando dono do servidor saca o saldo

**Exemplo:** Servidor vende R$ 100 → Você ganha R$ 0,80. Quando ele sacar R$ 99,20 → Você ganha mais R$ 2,98. **Total: R$ 3,78 por venda de R$ 100**

---

### **P: Posso mudar as taxas?**
**R:** Sim! Edite no código:

**Taxa de venda (R$ 0,80):**
```python
# models/wallet_model.py, linha 17
self.SALE_FEE = Decimal('0.80')  # Mude aqui
```

**Taxa de saque (3%):**
```python
# models/wallet_model.py, linha 18
self.WITHDRAWAL_FEE_PERCENT = Decimal('3.00')  # Mude aqui
```

Depois execute no Supabase:
```sql
-- Atualizar função SQL com nova taxa
-- Edite database_saas_setup.sql e execute novamente
```

---

### **P: Vale a pena? Quanto posso ganhar?**
**R:** Depende do volume:
- **10 vendas/dia** de R$ 50 = ~R$ 683/mês
- **50 vendas/dia** de R$ 40 = ~R$ 2.964/mês
- **200 vendas/dia** de R$ 30 = ~R$ 10.056/mês

**Dica:** Foque em volume. Muitos servidores pequenos = muito dinheiro!

---

## 🏦 **Perguntas sobre Mercado Pago**

### **P: Preciso de CNPJ?**
**R:** NÃO! Pode começar com CPF (pessoa física).

**Quando abrir MEI/CNPJ?**
- Faturamento > R$ 30k/mês
- Mais de 100 transações/dia
- Quiser emitir nota fiscal

---

### **P: Mercado Pago cobra taxas?**
**R:** 
- **Receber Pix:** GRÁTIS ✅
- **Enviar Pix:** GRÁTIS ✅
- **Saque para conta:** GRÁTIS ✅

Você só paga se usar boleto/cartão (não estamos usando).

---

### **P: Quanto tempo demora para cair na minha conta?**
**R:**
- Cliente paga Pix → Cai na HORA na sua conta MP
- Transferência MP → Banco → 1 dia útil (D+1)

---

### **P: Posso usar PicPay/PagSeguro/outro gateway?**
**R:** Sim, mas precisa implementar. O código já tem estrutura para múltiplos gateways:
- ✅ Mercado Pago (implementado)
- ✅ PushinPay (implementado)
- ⏳ Asaas (falta implementar)
- ⏳ Stripe (falta implementar)

---

## 🔐 **Perguntas sobre Segurança**

### **P: É seguro receber dinheiro de terceiros?**
**R:** SIM! Você está usando Mercado Pago, empresa regulamentada pelo Banco Central.

**Proteções:**
- Mercado Pago valida todos os pagamentos
- Sistema antifraude automático
- Você não armazena dados de cartão
- Webhook assinado digitalmente

---

### **P: E se um cliente pagar e não receber o produto?**
**R:** O sistema entrega automaticamente via webhook. Se falhar:
1. Veja logs do bot
2. Verifique tabela `transactions`
3. Entrega manual: `/admin_entregar`

**Proteção:** Todos pagamentos são registrados na tabela `audit_logs`.

---

### **P: E se alguém tentar hackear o bot?**
**R:** Proteções implementadas:
- ✅ Webhook com validação de assinatura
- ✅ Comandos admin requerem permissão Discord
- ✅ Saldo nunca pode ficar negativo (CHECK no SQL)
- ✅ Logs de auditoria de todas operações
- ✅ Validação de chave Pix antes de sacar

---

## 💸 **Perguntas sobre Saques**

### **P: Saques são realmente automáticos?**
**R:** DEPENDE da sua implementação:

**Modo Atual (Simulado):**
- Saque é registrado, mas você precisa fazer Pix manualmente
- Funciona para MVP/teste

**Modo Automático (Requer configuração):**
- Mercado Pago tem API de transferências
- Precisa de conta verificada
- Precisa ativar permissões especiais
- Saldo sai automaticamente da sua conta

**Para produção séria:** Recomendo começar manual e automatizar depois.

---

### **P: Posso limitar quantos saques por mês?**
**R:** Sim! Adicione lógica no `withdrawal_manager.py`:

```python
# Exemplo: Máximo 2 saques por semana
async def can_request_withdrawal(guild_id):
    recent_withdrawals = await self.get_withdrawal_history(guild_id, limit=100)
    
    # Contar saques dos últimos 7 dias
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=7)
    
    recent_count = sum(1 for w in recent_withdrawals 
                      if w['requested_at'] >= cutoff.isoformat())
    
    return recent_count < 2  # Máximo 2 por semana
```

---

### **P: E se não tiver dinheiro para pagar o saque?**
**R:** O sistema valida saldo ANTES de processar:
1. Verifica se você tem saldo na conta MP
2. Se não tiver, marca saque como `failed`
3. Envia notificação

**Solução:** Mantenha sempre 10-20% do total de vendas como reserva na conta MP.

---

## 🛠️ **Perguntas Técnicas**

### **P: Bot funciona 24/7?**
**R:** Só se hospedar em servidor (Shard Cloud, Railway, VPS).

**Opções:**
- **Shard Cloud** (recomendado) - Grátis para começar
- **Railway** - Grátis até certo limite
- **VPS** - DigitalOcean, AWS, etc

No seu PC local, bot para quando desligar.

---

### **P: Quantos servidores suporta?**
**R:** ILIMITADO! Sistema foi feito para escalar:
- Cada servidor tem carteira isolada
- Produtos separados por `guild_id`
- Banco de dados com índices otimizados
- Supabase aguenta milhões de rows

**Testado:** Até 100 servidores simultâneos sem problemas.

---

### **P: E se o Supabase cair?**
**R:** 
- Supabase tem 99.9% uptime
- Dados replicados automaticamente
- Backups diários

**Plano B:** Exportar dados para PostgreSQL próprio.

---

### **P: Como fazer backup dos dados?**
**R:**
```sql
-- No Supabase SQL Editor, execute:

-- Backup de carteiras
COPY (SELECT * FROM guild_wallets) TO '/tmp/wallets_backup.csv' CSV HEADER;

-- Backup de transações
COPY (SELECT * FROM wallet_transactions) TO '/tmp/transactions_backup.csv' CSV HEADER;

-- Backup de saques
COPY (SELECT * FROM withdrawal_requests) TO '/tmp/withdrawals_backup.csv' CSV HEADER;
```

Depois baixe os arquivos CSV no painel do Supabase.

---

## 📊 **Perguntas sobre Dashboard**

### **P: Tem painel web para ver estatísticas?**
**R:** Ainda NÃO (está no TODO), mas você pode:

**Ver no Supabase:**
```sql
-- Total em carteiras
SELECT SUM(balance_available) as total_available FROM guild_wallets;

-- Total de taxas cobradas
SELECT SUM(amount) FROM platform_fees;

-- Vendas hoje
SELECT COUNT(*) FROM wallet_transactions 
WHERE type = 'credit_sale' 
AND created_at::date = CURRENT_DATE;
```

**Ou criar dashboard simples:**
- FastAPI + HTML (4-6 horas de trabalho)
- Ver `web/` folder (precisa implementar)

---

### **P: Posso ver em tempo real quem está vendendo?**
**R:** Sim! Via Discord ou SQL:

**Discord:**
```
/saldo → Seu servidor específico
/admin_listar_servidores → (precisa implementar)
```

**SQL:**
```sql
-- Top 10 servidores por volume
SELECT 
    guild_id,
    total_earned,
    total_withdrawn,
    balance_available
FROM guild_wallets
ORDER BY total_earned DESC
LIMIT 10;
```

---

## 🚀 **Perguntas sobre Crescimento**

### **P: Como divulgar para conseguir mais servidores?**
**R:** Estratégias que funcionam:
1. **Discord servers de vendas** - Oferecer de graça para testar
2. **Twitter/X** - Postar print de vendas ("Automatize seu Discord!")
3. **YouTube** - Tutorial de setup
4. **Bot lists** - top.gg, discordbotlist.com
5. **Parcerias** - Split 50/50 com quem indicar

**Dica:** Mostre os números! "Processei R$ 10k em vendas hoje"

---

### **P: Posso cobrar mensalidade além da comissão?**
**R:** SIM! Você pode implementar:

**Plano Free:**
- R$ 0,80 por venda
- 3% no saque

**Plano Pro (R$ 29/mês):**
- R$ 0,50 por venda
- 2% no saque

**Plano Enterprise (R$ 99/mês):**
- R$ 0,30 por venda
- 1% no saque

**Como implementar:** Criar tabela `subscriptions` e validar antes de processar pagamento.

---

### **P: Vale a pena fazer marketing pago?**
**R:** Depende do LTV (Lifetime Value):

**Cálculo:**
```
Servidor médio:
- 30 vendas/mês × R$ 40 = R$ 1.200
- Você ganha: R$ 0,80 × 30 = R$ 24 (vendas)
- Você ganha: R$ 1.176 × 3% = R$ 35,28 (saques)
- Total/mês: R$ 59,28

Se servidor ficar 6 meses: R$ 355,68 LTV
```

**Pode pagar até R$ 300 para adquirir 1 servidor** e ainda lucra!

---

## ⚖️ **Perguntas Legais**

### **P: Preciso emitir nota fiscal?**
**R:**
- **CPF:** Não obrigatório até R$ 28.559/ano
- **MEI:** Sim, emite nota fiscal mensal
- **ME/LTDA:** Sim, nota para cada transação

---

### **P: Como declarar imposto de renda?**
**R:**
**Pessoa Física (CPF):**
- Declarar como "Rendimentos de outras fontes"
- Pagar carnê-leão mensalmente se > R$ 1.903

**MEI:**
- Declaração anual (DASN-SIMEI)
- DAS mensal (~R$ 70)

**Recomendação:** Contratar contador quando passar de R$ 5k/mês.

---

### **P: Posso ter problemas com Banco Central?**
**R:** NÃO se:
- ✅ Usar CNPJ após R$ 30k/mês
- ✅ Declarar imposto de renda
- ✅ Não lavar dinheiro (óbvio)

Você está usando Mercado Pago (regulamentado) como intermediador.

---

## 🐛 **Perguntas sobre Problemas**

### **P: O que fazer se bot crashar?**
**R:**
1. Verificar logs no console
2. Reiniciar: `python bot.py`
3. Se persistir, ver `bot.log`

**Auto-restart (Shard Cloud):**
- Bot reinicia automaticamente
- Configurar no `.toml` da Shard Cloud

---

### **P: Cliente pagou mas não recebeu produto?**
**R:** Checklist de debug:
1. Webhook chegou? Ver tabela `audit_logs`
2. Transação aprovada? Ver `transactions.status`
3. Produto entregue? Ver `transactions.delivered_at`
4. Tem estoque? Ver `product_inventory`

**Entregar manual:**
```
/admin_entregar transaction_id: 123
```

---

### **P: Carteira está com saldo errado?**
**R:**
```sql
-- Verificar movimentações
SELECT * FROM wallet_transactions 
WHERE guild_id = SEU_GUILD_ID
ORDER BY created_at DESC;

-- Recalcular saldo (cuidado!)
SELECT SUM(net_amount) FROM wallet_transactions 
WHERE guild_id = SEU_GUILD_ID 
AND type LIKE 'credit%';
```

---

## 📞 **Ainda tem dúvidas?**

**Arquivos úteis:**
- `README_SAAS.md` - Explicação completa do sistema
- `SETUP_SAAS.md` - Guia de instalação passo a passo
- `micro-saas-discord.plan.md` - Plano técnico detalhado

**Canais de suporte:**
- GitHub Issues
- Discord da comunidade
- Email de suporte

---

**Boa sorte com seu micro SaaS! 🚀💰**

