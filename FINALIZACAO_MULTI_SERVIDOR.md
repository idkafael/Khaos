# 🎯 Finalização do Sistema Multi-Servidor

## ✅ PROGRESSO ATUAL: 70%

### O QUE ESTÁ PRONTO:

1. ✅ **Banco de Dados** - 100%
   - SQL completo em `database_multiserver_setup.sql`
   - Tabela `guild_config`
   - Colunas `guild_id` em todas as tabelas

2. ✅ **Models** - 100%
   - `GuildConfigModel` - gerenciamento de configs
   - `ProductModel` - filtrado por servidor
   - `CouponModel` - filtrado por servidor
   - `InventoryModel` - filtrado por servidor

3. ✅ **Permissões** - 100%
   - Sistema de permissões implementado
   - Decorators prontos

4. ✅ **Comandos Admin** - 70%
   - Comandos criados em `commands/admin_multiserver_commands.py`
   - Precisa integrar no `bot.py`

---

## 📋 PASSO A PASSO PARA FINALIZAR

### PASSO 1: Executar SQL no Supabase ⚠️ CRÍTICO

1. Acesse: https://supabase.com/dashboard
2. SQL Editor → New query
3. Cole todo o conteúdo de `database_multiserver_setup.sql`
4. Clique em **RUN**

5. **Migrar dados existentes:**

```sql
-- SUBSTITUA 123456789 pelo ID do seu servidor Discord principal
UPDATE products SET guild_id = 123456789 WHERE guild_id IS NULL;
UPDATE coupons SET guild_id = 123456789 WHERE guild_id IS NULL;
UPDATE product_inventory SET guild_id = 123456789 WHERE guild_id IS NULL;

-- Tornar guild_id obrigatório
ALTER TABLE products ALTER COLUMN guild_id SET NOT NULL;
ALTER TABLE coupons ALTER COLUMN guild_id SET NOT NULL;
ALTER TABLE product_inventory ALTER COLUMN guild_id SET NOT NULL;
```

**Como obter o Guild ID:**
- Discord → Servidor → Botão direito → Copiar ID do Servidor

---

### PASSO 2: Atualizar bot.py

#### 2.1 Adicionar Imports

No início do `bot.py`, adicionar:

```python
from utils.permissions import require_server_admin, require_guild
from models.guild_config_model import GuildConfigModel
```

#### 2.2 Integrar Comandos Admin

Copiar os comandos de `commands/admin_multiserver_commands.py` para o `bot.py`:

```python
# Comando Criar Produto
@bot.tree.command(name="admin_criar_produto", description="[ADMIN] Criar um produto no servidor")
@require_server_admin()
@app_commands.describe(
    nome="Nome do produto",
    preco="Preço em R$",
    descricao="Descrição do produto",
    categoria="Categoria"
)
async def admin_criar_produto(
    interaction: discord.Interaction,
    nome: str,
    preco: float,
    descricao: str,
    categoria: str = "produto"
):
    # Copiar código de admin_multiserver_commands.py
    pass

# Repetir para outros comandos:
# - admin_criar_vip
# - admin_listar_produtos
# - admin_deletar_produto
# - admin_configurar
```

#### 2.3 Atualizar Comandos Existentes

**IMPORTANTE:** Atualizar comandos para filtrar por `guild_id`:

```python
# ANTES:
@bot.tree.command(name="produtos")
async def produtos_slash(interaction):
    products = await product_model.get_all_products()  # ❌ ERRADO
    
# DEPOIS:
@bot.tree.command(name="produtos")
async def produtos_slash(interaction):
    products = await product_model.get_products_by_guild(interaction.guild_id)  # ✅ CORRETO
```

**Comandos para atualizar:**
- `/setup_ticket` - linha que busca produtos
- `/produtos` - listar produtos
- `/comprar` - validar produto
- `/criar_cupom` - criar cupom
- `/listar_cupons` - listar cupons
- `/adicionar_estoque` - adicionar estoque

---

### PASSO 3: Testar Isolamento Entre Servidores

1. **Servidor A:**
   ```
   /admin_criar_produto
   Nome: Teste Servidor A
   Preço: 10
   ```

2. **Servidor B:**
   ```
   /produtos
   → Não deve mostrar "Teste Servidor A"
   ```

3. **Servidor B:**
   ```
   /admin_criar_produto
   Nome: Teste Servidor B
   Preço: 20
   ```

4. **Verificar:**
   - Servidor A vê apenas "Teste Servidor A"
   - Servidor B vê apenas "Teste Servidor B"

---

### PASSO 4: Configurar Split de Pagamento (Opcional)

Se você quer receber uma porcentagem de cada venda:

1. **Configure sua conta na PushinPay como recipient**

2. **Para cada servidor:**
   ```sql
   UPDATE guild_config 
   SET 
       pushinpay_split_percent = 10,  -- 10% para você
       pushinpay_split_recipient_id = 'seu_recipient_id_pushinpay'
   WHERE guild_id = ID_DO_SERVIDOR;
   ```

3. **Atualizar PaymentUtils (PENDENTE)**
   - Arquivo: `utils/payment_utils.py`
   - Adicionar lógica de split no pagamento

---

## 🔧 COMANDOS DISPONÍVEIS APÓS IMPLEMENTAÇÃO

### Comandos Admin:

```
/admin_criar_produto       - Criar produto normal
/admin_criar_vip           - Criar produto VIP
/admin_listar_produtos     - Ver produtos do servidor
/admin_deletar_produto     - Deletar produto
/admin_configurar          - Ver configuração do servidor
```

### Comandos Usuários (sem mudança):

```
/produtos                  - Ver produtos (do servidor atual)
/comprar                   - Comprar produto
/status                    - Status do pagamento
/meu_vip                   - Ver VIP (do servidor atual)
```

---

## ⚠️ BREAKING CHANGES

**ATENÇÃO:** Após executar a migração:

1. ❌ **Produtos antigos sem guild_id** não vão aparecer
   - Solução: Execute a migração SQL corretamente

2. ❌ **Comandos que não foram atualizados** vão dar erro
   - Solução: Atualize TODOS os comandos que usam ProductModel, CouponModel, InventoryModel

3. ❌ **Sistema de split** ainda não está implementado
   - Solução: Implementar lógica no PaymentUtils (próximo passo)

---

## 📊 CHECKLIST DE VERIFICAÇÃO

- [ ] SQL executado no Supabase
- [ ] Dados migrados para seu servidor principal
- [ ] Comandos admin integrados no bot.py
- [ ] Comandos existentes atualizados com guild_id
- [ ] Testado isolamento entre servidores
- [ ] Bot reiniciado e comandos sincronizados
- [ ] Split configurado (se usar)

---

## 🆘 RESOLUÇÃO DE PROBLEMAS

### Erro: "column guild_id does not exist"
**Causa:** SQL não foi executado no Supabase  
**Solução:** Execute `database_multiserver_setup.sql`

### Erro: "null value in column guild_id"
**Causa:** Dados antigos não foram migrados  
**Solução:** Execute o UPDATE para migrar dados

### Produtos não aparecem em nenhum servidor
**Causa:** guild_id não foi setado nos dados antigos  
**Solução:** Execute a migração SQL com o ID correto

### Comandos admin não aparecem
**Causa:** Decorators não foram aplicados  
**Solução:** Adicione `@require_server_admin()` em cada comando

---

## 🎯 PRÓXIMOS PASSOS OPCIONAIS

1. **Implementar Split de Pagamento**
   - Atualizar `utils/payment_utils.py`
   - Adicionar splits nos pagamentos PushinPay

2. **Criar Comandos de Configuração Avançada**
   - `/admin_set_api_key` - Definir API key própria
   - `/admin_set_split` - Configurar split
   - `/admin_set_admin_roles` - Definir roles admin

3. **Dashboard Web** (futuro)
   - Interface web para gerenciar produtos
   - Estatísticas por servidor
   - Gerenciamento de múltiplos servidores

---

## 📝 NOTAS IMPORTANTES

1. **Backup**: SEMPRE faça backup antes de migrar
2. **Testes**: Teste em servidor de desenvolvimento primeiro
3. **Guild ID**: Use o ID correto do seu servidor principal
4. **Permissões**: Bot precisa estar acima das roles VIP

---

**Status Atual**: 70% implementado, 30% falta (integração no bot.py e testes)  
**Tempo estimado para conclusão**: 1-2 horas

**Arquivos modificados nesta implementação:**
- `database_multiserver_setup.sql` ✅
- `models/guild_config_model.py` ✅
- `models/product_model.py` ✅
- `models/coupon_model.py` ✅
- `models/inventory_model.py` ✅
- `utils/permissions.py` ✅
- `commands/admin_multiserver_commands.py` ✅
- `bot.py` ⏳ (pendente integração)
- `utils/payment_utils.py` ⏳ (pendente split)
- `README.md` ⏳ (pendente documentação)

