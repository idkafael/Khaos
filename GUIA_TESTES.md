# 🧪 Guia de Testes - Sistema Micro SaaS

## 📋 Checklist

Execute **EM ORDEM**:

- [ ] **Passo 1:** Testar comando `/saldo` no Discord
- [ ] **Passo 2:** Adicionar colunas no banco (SQL 1)
- [ ] **Passo 3:** Simular venda de R$ 100 (SQL 2)
- [ ] **Passo 4:** Verificar saldo no Discord
- [ ] **Passo 5:** Testar `/configurar_pix`
- [ ] **Passo 6:** Testar `/solicitar_saque`

---

## 🎮 Passo 1: Testar `/saldo` no Discord

1. Aguarde **1-2 minutos** para o deploy terminar na Shard Cloud
2. No seu servidor Discord, digite: `/saldo`
3. **Resultado esperado:**

```
💰 Carteira do Servidor
Saldo Disponível: R$ 0.00
Saldo Pendente: R$ 0.00
Total Ganho: R$ 0.00
Total Sacado: R$ 0.00
Taxas Pagas: R$ 0.00
Lucro Líquido: R$ 0.00

⚠️ Chave Pix: Use /configurar_pix para cadastrar
```

✅ **Se aparecer esta mensagem:** Prossiga para o Passo 2  
❌ **Se der erro:** Me envie a mensagem de erro completa

---

## 🗄️ Passo 2: Adicionar colunas na tabela transactions

1. Abra o **Supabase** → **SQL Editor**
2. Cole o conteúdo do arquivo: `database_add_columns_transactions.sql`
3. Clique em **Run**
4. **Resultado esperado:** "Success. No rows returned"

---

## 💰 Passo 3: Simular venda de R$ 100,00

1. Ainda no **SQL Editor** do Supabase
2. Cole o conteúdo da **SEÇÃO 3** do arquivo: `database_test_complete.sql`
3. Clique em **Run**
4. **Resultado esperado no log:**

```
NOTICE: ✅ Transação criada: ID 123
NOTICE: ✅ Carteira creditada: R$ 99.20 (líquido)
NOTICE: ✅ Movimentação registrada na carteira
NOTICE: ✅ Taxa registrada: R$ 0.80
NOTICE: 🎉 TESTE COMPLETO! Verifique o saldo no Discord com /saldo
```

---

## 🎮 Passo 4: Verificar saldo atualizado

1. Volte ao Discord
2. Digite: `/saldo`
3. **Resultado esperado:**

```
💰 Carteira do Servidor
Saldo Disponível: R$ 99.20  ← Venda de R$ 100 - R$ 0,80 taxa
Saldo Pendente: R$ 0.00
Total Ganho: R$ 99.20
Total Sacado: R$ 0.00
Taxas Pagas: R$ 0.80
Lucro Líquido: R$ 99.20
```

✅ **Se o saldo apareceu:** Sistema funcionando! Continue para Passo 5  
❌ **Se ainda está R$ 0,00:** Execute a SEÇÃO 4 do `database_test_complete.sql` e me envie o resultado

---

## 🔑 Passo 5: Configurar chave Pix

1. No Discord, digite: `/configurar_pix`
2. Preencha o modal:
   - **Tipo:** CPF
   - **Chave Pix:** Digite um CPF válido (pode ser fake para teste: 111.111.111-11)
3. **Resultado esperado:**

```
✅ Chave Pix cadastrada com sucesso!
Tipo: CPF
Chave: 111.111.111-11

Agora você pode solicitar saques usando /solicitar_saque
Saque mínimo: R$ 10,00
Taxa de saque: 3%
```

---

## 💸 Passo 6: Testar solicitação de saque

1. No Discord, digite: `/solicitar_saque`
2. Preencha o modal:
   - **Valor:** 50
3. **Resultado esperado:**

```
💰 Solicitação de Saque Criada

Valor solicitado: R$ 50,00
Taxa (3%): R$ 1,50
Você receberá: R$ 48,50

Chave Pix: 111.111.111-11 (CPF)
Status: ⏳ Processando

O saque será processado em até 24 horas.
Você receberá uma DM quando for concluído.
```

4. Digite `/saldo` novamente
5. **Resultado esperado:**

```
Saldo Disponível: R$ 49.20  ← Era R$ 99,20 - R$ 50,00 sacados
Saldo Pendente: R$ 0.00
Total Sacado: R$ 50.00  ← Atualizado!
Taxas Pagas: R$ 2.30  ← R$ 0,80 (venda) + R$ 1,50 (saque)
```

---

## ✅ Teste Completo!

Se todos os passos funcionaram, o sistema está 100% operacional! 🎉

### O que foi testado:

✅ Criação de carteira virtual  
✅ Registro de venda com taxa de R$ 0,80  
✅ Cálculo correto de saldo líquido  
✅ Configuração de chave Pix  
✅ Solicitação de saque com taxa de 3%  
✅ Atualização automática de saldo  
✅ Histórico de transações  

---

## 🧹 Limpar dados de teste (Opcional)

Se quiser resetar tudo e testar novamente:

1. Cole a **SEÇÃO 7** do arquivo `database_test_complete.sql`
2. Descomente as linhas (remova os `--` do início)
3. Execute

---

## 📞 Próximos Passos

Depois dos testes, podemos:

1. **Criar uma venda REAL** via Mercado Pago (sandbox)
2. **Processar webhook** de pagamento aprovado
3. **Executar saque real** via API do Mercado Pago
4. **Ativar modo produção** com credenciais reais

---

## 🆘 Se algo não funcionar

Me envie:

1. Qual passo deu erro
2. A mensagem de erro completa
3. Print do resultado do SQL (se aplicável)

