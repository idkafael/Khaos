# Sistema VIP - Documentação Completa

## Visão Geral

O Sistema VIP permite gerenciar assinaturas premium no Discord com roles temporárias ou vitalícias, controle automático de expiração e notificações via DM.

## Fluxo de Funcionamento

### 1. Compra de VIP

```
Cliente → Abre Ticket → Escolhe Produto VIP → Paga via Pix → Sistema Detecta Pagamento
  → Adiciona Role Automaticamente → Cria Registro no Banco → Envia DM de Boas-vindas
```

### 2. Expiração de VIP

```
Task a cada 6h → Busca Assinaturas Expiradas → Remove Role → Marca como Expirado
  → Envia DM de Expiração
```

### 3. Aviso de Expiração

```
Task a cada 6h → Busca Assinaturas Próximas de Expirar (3 dias) → Envia DM de Aviso
```

## Estrutura do Banco de Dados

### Tabela `vip_subscriptions`

```sql
CREATE TABLE vip_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,           -- ID do usuário Discord
    guild_id BIGINT NOT NULL,          -- ID do servidor
    role_id BIGINT NOT NULL,           -- ID da role VIP
    role_name VARCHAR(100) NOT NULL,   -- Nome da role (Bronze, Prata, etc)
    duration_days INTEGER NULL,        -- NULL = vitalício
    started_at TIMESTAMP NOT NULL,     -- Data de início
    expires_at TIMESTAMP NULL,         -- NULL = vitalício
    status VARCHAR(20) NOT NULL,       -- active, expired, cancelled
    transaction_id INTEGER NULL,       -- Relaciona com transação
    product_id INTEGER NOT NULL,       -- ID do produto VIP
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Tabela `products` - Campo Adicional

```sql
ALTER TABLE products 
ADD COLUMN vip_config JSONB DEFAULT NULL;
```

**Exemplo de `vip_config`:**
```json
{
  "role_name": "VIP Bronze",
  "duration_days": 30,
  "benefits": ["Acesso a canais exclusivos", "Prioridade em suporte"]
}
```

## Produtos VIP Disponíveis

### VIP Bronze
- **1 Dia** - R$ 5,00
- **15 Dias** - R$ 25,00
- **30 Dias** - R$ 45,00

### VIP Prata
- **30 Dias** - R$ 75,00

### VIP Ouro
- **30 Dias** - R$ 120,00

### VIP Diamante
- **Vitalício** - R$ 500,00

## Comandos Disponíveis

### Comandos de Usuário

#### `/meu_vip`
Ver status da assinatura VIP atual
- Mostra: role, data de início, data de expiração, dias restantes
- Exibe benefícios ativos

#### `/renovar_vip`
Ver planos VIP disponíveis para compra/renovação
- Lista todos os planos por categoria
- Mostra preços e durações
- Instruções de como comprar

#### `/historico_vip`
Ver histórico completo de assinaturas
- Mostra todas as assinaturas (ativas, expiradas, canceladas)
- Limitado a 10 mais recentes

### Comandos Admin

#### `/listar_vips`
Listar todos os VIPs ativos do servidor
- Agrupa por role
- Mostra dias restantes
- Total de VIPs por categoria

#### `/adicionar_vip <membro> <role_vip> [duracao_dias]`
Adicionar VIP manualmente a um usuário
- `duracao_dias` é opcional (omita para vitalício)
- Cria role se não existir
- Envia DM de boas-vindas automaticamente

**Exemplo:**
```
/adicionar_vip @João VIP Ouro 30
/adicionar_vip @Maria VIP Diamante  (vitalício)
```

#### `/remover_vip <membro>`
Remover VIP de um usuário
- Remove a role
- Cancela assinatura no banco
- Não envia DM (remoção manual)

#### `/vip_stats`
Ver estatísticas de VIPs do servidor
- Total de VIPs ativos
- Total de VIPs expirados
- Quantidade de vitalícios
- Distribuição por role

## Arquitetura do Sistema

### Arquivos Criados

1. **`models/vip_model.py`** - Model de assinaturas VIP
   - CRUD de assinaturas
   - Verificação de expirações
   - Estatísticas

2. **`utils/vip_manager.py`** - Gerenciador de roles e notificações
   - Adicionar/remover roles
   - Enviar DMs (boas-vindas, avisos, expiração)
   - Processar compras VIP
   - Criar roles automaticamente

3. **`database_vip_setup.sql`** - SQL para criar tabela
   - Estrutura completa
   - Índices otimizados
   - Triggers automáticos

### Arquivos Modificados

1. **`bot.py`**
   - Produtos VIP adicionados
   - Task periódica de verificação (6 em 6 horas)
   - Comandos de usuário e admin
   - Inicialização do VipModel

2. **`utils/delivery_manager.py`**
   - Detecção de produtos VIP
   - Integração com VipManager
   - Processamento de entrega VIP

## Configurações Necessárias

### Permissões do Bot

O bot precisa das seguintes permissões:
- ✅ **Manage Roles** (Gerenciar Cargos)
- ✅ **Create Roles** (opcional, para criar roles automaticamente)
- ✅ A role do bot deve estar ACIMA das roles VIP na hierarquia

### Configuração de Roles

O bot pode criar roles automaticamente com cores predefinidas:
- **VIP Bronze**: Bronze (RGB 205, 127, 50)
- **VIP Prata**: Prata (RGB 192, 192, 192)
- **VIP Ouro**: Ouro (RGB 255, 215, 0)
- **VIP Platina**: Platina (RGB 229, 228, 226)
- **VIP Diamante**: Diamante (RGB 185, 242, 255)

## Task Automática de Verificação

A task `check_vip_expirations` roda **a cada 6 horas** e:

1. **Expira assinaturas vencidas:**
   - Busca assinaturas com `expires_at < now()`
   - Remove role do usuário
   - Marca como `expired` no banco
   - Envia DM informando expiração

2. **Avisa assinaturas próximas de expirar:**
   - Busca assinaturas que expiram em 3 dias
   - Envia DM de aviso
   - Oferece opção de renovação

## Notificações via DM

### DM de Boas-vindas
Enviada automaticamente quando VIP é ativado:
- Informações da role
- Duração da assinatura
- Data de expiração
- Benefícios incluídos

### DM de Aviso de Expiração
Enviada 3 dias antes da expiração:
- Dias restantes
- Data de expiração
- Instruções para renovar

### DM de Expiração
Enviada quando VIP expira:
- Confirmação de expiração
- Benefícios perdidos
- Como reativar/renovar

**Nota:** Se o usuário tiver DMs desabilitadas, as mensagens não serão enviadas, mas o sistema continuará funcionando normalmente.

## Benefícios VIP

Todos os VIPs recebem:
- ✨ Acesso a canais exclusivos VIP
- 🎯 Prioridade no suporte
- 💰 Descontos especiais
- 🎁 Conteúdo exclusivo

## Comportamento de Renovação

- Cliente precisa comprar novamente manualmente
- Sistema detecta se já tem VIP ativo
- Ao comprar novo VIP, o anterior é cancelado
- Nova assinatura começa imediatamente

## Troubleshooting

### Role não foi adicionada
- Verificar permissões do bot
- Verificar hierarquia de roles (bot precisa estar acima)
- Checar logs do console

### DM não foi enviada
- Normal se usuário tiver DMs desabilitadas
- Sistema funciona mesmo sem DM
- Role é adicionada normalmente

### VIP não expirou automaticamente
- Task roda a cada 6 horas
- Pode ter delay de até 6 horas
- Verificar se bot está online
- Checar logs da task

### Produto VIP não detectado
- Verificar se `category` = "VIP"
- Verificar se tem campo `vip_config`
- Checar se `vip_config` tem `role_name` e `duration_days`

## Manutenção

### Verificar assinaturas ativas
```sql
SELECT * FROM vip_subscriptions 
WHERE status = 'active' 
ORDER BY expires_at;
```

### Buscar assinaturas de um usuário
```sql
SELECT * FROM vip_subscriptions 
WHERE user_id = <user_id> 
ORDER BY created_at DESC;
```

### Estatísticas gerais
```sql
SELECT 
    status,
    COUNT(*) as total
FROM vip_subscriptions
GROUP BY status;
```

## Logs do Sistema

Todas as operações VIP são registradas no console:
- `✅ Assinatura VIP criada`
- `👑 VIP processado com sucesso`
- `🔻 Role removida`
- `⏰ Transação marcada como expirada`
- `📬 DM de boas-vindas VIP enviada`

## Futuras Melhorias

Possíveis adições ao sistema:
- [ ] Renovação automática recorrente
- [ ] Sistema de upgrades (Bronze → Prata → Ouro)
- [ ] Programa de fidelidade/pontos
- [ ] Relatórios mensais de vendas VIP
- [ ] Controle de avisos enviados (evitar spam)
- [ ] Canal de logs admin específico para VIP
- [ ] Webhooks de notificação para admins
- [ ] Dashboard web para gerenciamento

## Suporte

Para problemas ou dúvidas:
1. Verificar logs do console
2. Consultar esta documentação
3. Revisar configurações do banco de dados
4. Verificar permissões do bot no Discord


