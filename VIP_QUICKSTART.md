# Sistema VIP - Guia de Instalação Rápida

## 📋 Checklist de Instalação

### 1. Configurar Banco de Dados

Execute o SQL no Supabase:

```bash
# No seu painel Supabase, vá em SQL Editor e execute:
```

```sql
-- Copie e cole o conteúdo completo de database_vip_setup.sql
```

**Ou execute diretamente:**
1. Acesse seu projeto no [Supabase](https://supabase.com)
2. Vá em **SQL Editor**
3. Cole o conteúdo de `database_vip_setup.sql`
4. Clique em **Run**

### 2. Configurar Permissões do Bot no Discord

No Discord Developer Portal:

1. Vá em **OAuth2** → **Bot**
2. Marque as permissões:
   - ✅ Manage Roles
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Manage Channels (para tickets)

3. **Importante:** No servidor Discord, arraste a role do bot **ACIMA** das roles VIP na hierarquia!

### 3. Verificar Arquivos

Certifique-se de que os arquivos foram criados:

```
✅ models/vip_model.py
✅ utils/vip_manager.py
✅ database_vip_setup.sql
✅ VIP_SYSTEM.md
```

E modificados:

```
✅ bot.py
✅ utils/delivery_manager.py
```

### 4. Reiniciar o Bot

```bash
# Pare o bot se estiver rodando
# Ctrl+C ou feche o terminal

# Inicie novamente
python bot.py
```

### 5. Verificar Inicialização

No console, procure por:

```
✅ Tabela de assinaturas VIP conectada com sucesso
📦 Carregando novos produtos digitais...
✅ X produtos digitais carregados com sucesso!
```

## 🧪 Testar o Sistema

### Teste 1: Verificar Produtos VIP

No Discord, execute:
```
/produtos
```

Você deve ver os produtos VIP listados na categoria "VIP":
- VIP Bronze - 1 Dia (R$ 5,00)
- VIP Bronze - 15 Dias (R$ 25,00)
- VIP Bronze - 30 Dias (R$ 45,00)
- VIP Prata - 30 Dias (R$ 75,00)
- VIP Ouro - 30 Dias (R$ 120,00)
- VIP Diamante - Vitalício (R$ 500,00)

### Teste 2: Adicionar VIP Manual (Admin)

```
/adicionar_vip @SeuNome "VIP Bronze" 7
```

Você deve:
1. Receber a role "VIP Bronze" automaticamente
2. Receber uma DM de boas-vindas
3. Ver a confirmação no canal

### Teste 3: Verificar Status VIP

```
/meu_vip
```

Deve mostrar suas informações de VIP:
- Role atual
- Dias restantes
- Data de expiração

### Teste 4: Ver Planos Disponíveis

```
/renovar_vip
```

Deve listar todos os planos VIP organizados por role.

### Teste 5: Compra Real (Teste Completo)

1. Crie um ticket de compra
2. No canal do ticket, use:
   ```
   /comprar VIP Bronze - 1 Dia
   ```
3. Pague via Pix (ou simule pagamento)
4. Quando o pagamento for detectado:
   - ✅ Role deve ser adicionada automaticamente
   - ✅ Registro criado no banco
   - ✅ DM de boas-vindas enviada
   - ✅ Confirmação no canal do ticket

## 🔍 Verificar Logs

Durante o teste, monitore o console para ver:

```
👑 Processando entrega VIP para transação #X
✅ Role VIP Bronze adicionada a SeuNome
✅ Assinatura VIP criada: VIP Bronze para usuário 123456789
📬 DM de boas-vindas VIP enviada para SeuNome
🎉 VIP processado com sucesso para SeuNome - VIP Bronze
✅ VIP entregue com sucesso para transação #X
```

## ⚙️ Comandos Admin Úteis

### Listar todos VIPs
```
/listar_vips
```

### Ver estatísticas
```
/vip_stats
```

### Adicionar VIP manual
```
/adicionar_vip @Usuário "VIP Ouro" 30
/adicionar_vip @Usuário "VIP Diamante"  (vitalício)
```

### Remover VIP
```
/remover_vip @Usuário
```

## 🕐 Sistema de Verificação Automática

O bot verifica automaticamente **a cada 6 horas**:
- Assinaturas expiradas (remove role e envia DM)
- Assinaturas próximas de expirar (envia aviso 3 dias antes)

No console você verá:
```
👑 VIP Check: 2 expirado(s), 5 próximo(s) de expirar
```

## ❗ Troubleshooting Rápido

### Role não foi adicionada

**Solução:**
1. Verificar hierarquia de roles (bot deve estar acima)
2. Verificar permissão "Manage Roles"
3. Recriar a role manualmente e tentar novamente

### DM não foi enviada

**Solução:**
- Normal! Usuário pode ter DMs desabilitadas
- O sistema funciona mesmo sem DM
- A role é adicionada normalmente

### Produto VIP não detectado

**Solução:**
1. Verificar se produto tem `category: "VIP"`
2. Verificar se tem campo `vip_config`
3. Recarregar produtos: `/reload_products` (admin)

### Tabela não existe no banco

**Solução:**
1. Execute `database_vip_setup.sql` no Supabase
2. Verifique se não há erros no SQL Editor
3. Reinicie o bot

## 📊 Consultas SQL Úteis

### Ver todas assinaturas ativas
```sql
SELECT 
    user_id,
    role_name,
    started_at,
    expires_at,
    EXTRACT(DAY FROM (expires_at - NOW())) as days_left
FROM vip_subscriptions
WHERE status = 'active'
ORDER BY expires_at;
```

### Ver histórico de um usuário
```sql
SELECT * FROM vip_subscriptions
WHERE user_id = 123456789
ORDER BY created_at DESC;
```

### Estatísticas gerais
```sql
SELECT 
    role_name,
    status,
    COUNT(*) as total
FROM vip_subscriptions
GROUP BY role_name, status
ORDER BY role_name, status;
```

## ✅ Checklist Final

Antes de colocar em produção:

- [ ] Banco de dados configurado (tabela vip_subscriptions)
- [ ] Permissões do bot configuradas
- [ ] Hierarquia de roles correta
- [ ] Bot reiniciado e produtos carregados
- [ ] Teste manual de adição VIP funcionando
- [ ] Teste de compra real funcionando
- [ ] DMs sendo enviadas (ou erro tratado se desabilitadas)
- [ ] Task automática rodando (verificar logs após 6h)
- [ ] Comandos admin funcionando
- [ ] Comandos de usuário funcionando

## 🎉 Pronto!

Seu sistema VIP está configurado e funcionando! 

Para mais detalhes, consulte:
- `VIP_SYSTEM.md` - Documentação completa
- `database_vip_setup.sql` - Estrutura do banco
- Logs do console - Monitoramento em tempo real

**Dica:** Configure um canal de logs para receber notificações automáticas de vendas VIP!


