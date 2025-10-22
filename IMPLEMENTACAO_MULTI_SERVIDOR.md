# 🚀 Implementação Multi-Servidor - Status e Próximos Passos

## ✅ O que já foi feito:

### 1. Banco de Dados
- ✅ Criado `database_multiserver_setup.sql` com:
  - Tabela `guild_config` para configurações por servidor
  - Colunas `guild_id` adicionadas em products, coupons, inventory
  - Índices compostos para performance
  - Triggers para updated_at

### 2. Models Criados/Atualizados
- ✅ `models/guild_config_model.py` - Gerenciamento de configurações
- ✅ `models/product_model.py` - Atualizado com filtro guild_id
- ✅ `utils/permissions.py` - Sistema de permissões

## ⏳ O que falta fazer:

### 3. Atualizar Models Restantes

**CouponModel** (`models/coupon_model.py`):
- Adicionar parâmetro `guild_id` em todos os métodos
- Filtrar cupons por servidor
- Validar uso de cupom apenas no servidor de origem

**InventoryModel** (`models/inventory_model.py`):
- Adicionar filtro `guild_id` em `get_available_items`
- Adicionar filtro `guild_id` em `reserve_item`
- Estoque completamente isolado por servidor

### 4. Criar Comandos Admin

Criar arquivo `commands/admin_commands.py` com:

```python
# Comandos para gerenciar produtos
@bot.tree.command(name="admin_criar_produto")
@require_server_admin()
async def admin_criar_produto(interaction: discord.Interaction):
    # Modal para criar produto
    pass

@bot.tree.command(name="admin_listar_produtos")
@require_server_admin()
async def admin_listar_produtos(interaction: discord.Interaction):
    # Listar produtos do servidor
    pass

@bot.tree.command(name="admin_editar_produto")
@require_server_admin()
async def admin_editar_produto(interaction: discord.Interaction, product_id: int):
    # Modal para editar produto
    pass

@bot.tree.command(name="admin_deletar_produto")
@require_server_admin()
async def admin_deletar_produto(interaction: discord.Interaction, product_id: int):
    # Deletar produto
    pass

# Comandos para configuração
@bot.tree.command(name="admin_configurar")
@require_server_admin()
async def admin_configurar(interaction: discord.Interaction):
    # Modal para configurar servidor
    pass
```

### 5. Atualizar Comandos Existentes

**No `bot.py`, atualizar:**

Comando `/setup_ticket`:
```python
# ANTES:
products = await product_model.get_all_products()

# DEPOIS:
products = await product_model.get_products_by_guild(interaction.guild_id)
```

Comando `/produtos`:
```python
# ANTES:
products = await product_model.get_all_products()

# DEPOIS:
products = await product_model.get_products_by_guild(interaction.guild_id)
```

Comando `/comprar`:
```python
# ANTES:
product = await product_model.get_product_by_id(product_id)

# DEPOIS:
product = await product_model.get_product_by_id(product_id, interaction.guild_id)
```

### 6. Atualizar PaymentUtils

Em `utils/payment_utils.py`:

```python
async def create_payment(self, guild_id: int, ...):
    # Buscar config do servidor
    guild_config = await GuildConfigModel().get_config(guild_id)
    
    # Usar API key específica ou global
    api_key = await GuildConfigModel().get_pushinpay_key(guild_id)
    
    # Adicionar split se configurado
    split = await GuildConfigModel().get_split_config(guild_id)
    if split:
        payment_data['splits'] = [{
            'recipient_id': split['recipient_id'],
            'percent': split['percent']
        }]
```

## 📋 Passos de Migração

### Passo 1: Executar SQL no Supabase
```sql
-- 1. Executar database_multiserver_setup.sql

-- 2. Migrar dados existentes para seu servidor principal
UPDATE products SET guild_id = SEU_GUILD_ID WHERE guild_id IS NULL;
UPDATE coupons SET guild_id = SEU_GUILD_ID WHERE guild_id IS NULL;
UPDATE product_inventory SET guild_id = SEU_GUILD_ID WHERE guild_id IS NULL;

-- 3. Tornar guild_id obrigatório
ALTER TABLE products ALTER COLUMN guild_id SET NOT NULL;
ALTER TABLE coupons ALTER COLUMN guild_id SET NOT NULL;
ALTER TABLE product_inventory ALTER COLUMN guild_id SET NOT NULL;
```

### Passo 2: Adicionar models ao __init__.py

Em `models/__init__.py`:
```python
from .guild_config_model import GuildConfigModel
```

### Passo 3: Importar permissões no bot.py

No início do `bot.py`:
```python
from utils.permissions import require_server_admin, require_guild, is_server_admin
from models.guild_config_model import GuildConfigModel
```

### Passo 4: Testar

1. Execute o SQL de migração
2. Reinicie o bot
3. Teste criar produto em Servidor A
4. Adicione bot em Servidor B
5. Verifique que produtos não aparecem em Servidor B

## 🔧 Como Usar Depois de Implementado

### Para Admins de Servidor:

1. **Configurar Servidor:**
```
/admin_configurar
```

2. **Criar Produto VIP:**
```
/admin_criar_vip
```

3. **Criar Produto Normal:**
```
/admin_criar_produto
```

4. **Listar Produtos:**
```
/admin_listar_produtos
```

### Para Usuários:

- Tudo funciona igual, mas veem apenas produtos do servidor atual
- Cupons só funcionam no servidor onde foram criados
- VIPs são isolados por servidor

## ⚠️ Importante

- **Backup**: Faça backup do banco antes de migrar
- **Testes**: Teste em servidor de desenvolvimento primeiro
- **Guild ID**: Substitua SEU_GUILD_ID pelo ID real do seu servidor
- **Permissões**: Bot precisa permissão de "Manage Roles" em todos os servidores

## 📊 Compatibilidade

O sistema é retrocompatível. Servidores sem configuração:
- Usam API key global do PushinPay
- Apenas admins Discord podem gerenciar produtos
- Tudo funciona normalmente

Servidores configurados:
- Podem ter API key própria (recebem pagamentos diretos)
- Ou usar split (% vai para o dono do bot)
- Admins customizáveis por roles

## 🎯 Próximas Tarefas Prioritárias

1. ⏳ Atualizar CouponModel com guild_id
2. ⏳ Atualizar InventoryModel com guild_id
3. ⏳ Criar comandos admin (admin_commands.py)
4. ⏳ Atualizar comandos existentes no bot.py
5. ⏳ Implementar split de pagamento no PaymentUtils
6. ⏳ Testar isolamento entre servidores
7. ⏳ Documentar no README

---

**Status**: 30% implementado. Base de dados e models principais prontos.
**Tempo estimado para conclusão**: 2-4 horas de trabalho focado.

