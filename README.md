# Bot de Vendas no Discord com Sistema de Tickets e Pagamento via Pix

Bot moderno de vendas no Discord com sistema de tickets automatizado, interface com botões e modals, comandos slash, e integração completa com **Supabase** e **PushinPay** para processamento de pagamentos via Pix.

---

## 📑 Índice de Conteúdo

### 🚀 Início Rápido
- [✅ Status de Configuração](#-status-de-configuração-atual)
- [🔧 Instalação](#-instalação)
- [⚙️ Configuração Completa](#️-configuração)
- [🗄️ Estrutura do Banco de Dados](#️-estrutura-do-banco-de-dados)

### 💎 Sistemas Principais
- [🎫 Funcionalidades](#-funcionalidades)
- [🎟️ Sistema de Cupons de Desconto](#️-sistema-de-cupons-de-desconto)
- [👑 Sistema VIP - Gerenciamento de Assinaturas](#-sistema-vip---gerenciamento-de-assinaturas)
- [🆘 Sistema de Suporte Customizado](#-sistema-de-suporte-customizado)

### 🎯 Guias Essenciais
- [🎯 Como Criar e Gerenciar Produtos VIP](#-como-criar-e-gerenciar-produtos-vip)
- [🎯 Como Usar o Sistema de Tickets](#-como-usar-o-sistema-de-tickets)
- [🔄 Fluxo do Bot](#-fluxo-do-bot)
- [🎮 Comandos do Bot](#-comandos-do-bot)

### 🚀 Deploy e Produção
- [✅ Checklist Completo de Deploy](#-checklist-completo-de-deploy)
- [🚀 Como Fazer Deploy na Shard Cloud](#-como-fazer-deploy-na-shard-cloud)
- [🚀 Executando o Bot](#-executando-o-bot)

### 📚 Referência Técnica
- [🏗️ Estrutura do Projeto](#️-estrutura-do-projeto)
- [📊 Produtos de Exemplo](#-produtos-de-exemplo)
- [🛡️ Segurança](#️-segurança)
- [🐛 Solução de Problemas](#-solução-de-problemas)
- [📝 Logs](#-logs)
- [🛠️ Tecnologias](#️-tecnologias)

### 📄 Informações
- [🤝 Contribuição](#-contribuição)
- [📄 Licença](#-licença)
- [📞 Suporte](#-suporte)
- [🔮 Roadmap](#-roadmap)

---

## ✅ STATUS DE CONFIGURAÇÃO ATUAL

### **Configurações Básicas - CONCLUÍDAS** ✅
- ✅ **Arquivo `.env` criado** com todas as credenciais
  - Discord Token: `842c8e29352ebd03e85b29f8c1c4ed6ee2e981194ad0236c153e3bb234c3848f`
  - Application ID: `784058182515425310`
  - Supabase URL: `https://sxsaxcqliuiolktypwkf.supabase.co`
  - PushinPay API Key: `50790|dakuggRtFoHjIZb2XpYYbDoa2exlT5NPspJayboI40bfb10f`
  - Sandbox Mode: `true`

- ✅ **Supabase Configurado** 
  - 3 tabelas criadas: `products`, `transactions`, `product_inventory`
  - Produtos cadastrados no banco de dados
  - Índices de performance aplicados

- ✅ **Bot Online e Funcionando**
  - Bot está rodando localmente
  - Pronto para receber comandos

### **Próximas Etapas - PENDENTES** ⏳
- ⏳ **Convidar Bot para Servidor**
  - Link: `https://discord.com/api/oauth2/authorize?client_id=784058182515425310&permissions=277025770576&scope=bot%20applications.commands`

- ⏳ **Configurar Sistema de Tickets no Discord**
  - Usar comando `/setup_ticket` no servidor
  - Configurar IDs opcionais no `.env`:
    - `TICKET_CATEGORY_ID` - Categoria para criar tickets
    - `ADMIN_ROLE_ID` - Cargo de administrador
    - `TICKET_LOGS_CHANNEL_ID` - Canal de logs

- ⏳ **Executar SQL de Cupons no Supabase**
  - Execute o arquivo `database_coupon_setup.sql` no SQL Editor
  - Isso criará as tabelas: `coupons` e `coupon_usage`
  - Atualizará a tabela `transactions` com campos de cupom

- ⏳ **Criar Cupons de Teste**
  - Use `/criar_cupom` no Discord para criar cupons
  - Exemplo: PRIMEIRACOMPRA (15% off, um por usuário)

- ⏳ **Adicionar Estoque de Produtos**
  - Usar `/adicionar_estoque` para adicionar códigos/keys
  - Adicionar produtos para: Minecraft, Spotify, Netflix, Discord Nitro, etc.

- ⏳ **Deploy em Produção (Opcional)**
  - Usar Shard Cloud para manter bot 24/7 online
  - Seguir instruções na seção "Deploy na Shard Cloud" abaixo

### **Novidades Recentes** 🆕

- ✅ **3 Melhorias de UX de Alto Impacto** - Implementado (24/10/2025)
  - 💳 **Botão "Gerar Pagamento"** - Zero digitação, apenas um clique!
  - ⏳ **Mensagens de Loading** - Feedback visual constante durante processamento
  - 🎉 **"Quase Lá!"** - Mensagem festiva após confirmação do pagamento
  - **Resultado:** +30% conversão estimada, experiência muito mais profissional

- ✅ **Comando `/comprar` Automático** - Implementado (24/10/2025)
  - Agora basta digitar `/comprar` sem parâmetros!
  - Bot detecta automaticamente o produto do ticket
  - Zero erros de digitação do nome do produto
  - UX super simplificada e intuitiva
  - Compatibilidade mantida: ainda aceita nome manual se quiser

- ✅ **Sistema Multi-Servidor** - Implementado (22/10/2025)
  - Cada servidor Discord gerencia **seus próprios produtos** independentemente
  - VIPs, cupons e estoque isolados por servidor
  - Comandos admin exclusivos: `/admin_criar_produto`, `/admin_criar_vip`, `/admin_listar_produtos`, `/admin_deletar_produto`
  - Produtos nunca se misturam entre servidores diferentes
  - Sistema completamente escalável para múltiplos servidores

- ✅ **Sistema de Estoque Ilimitado** - Implementado (22/10/2025)
  - Produtos VIP agora têm **estoque infinito** automaticamente
  - Novos produtos podem ser marcados como `unlimited_stock: True`
  - Ideal para roles, acessos e produtos digitais sem limite
  - Entrega automática sem necessidade de gerenciar inventory
  - Ícone ♾️ identifica produtos ilimitados

- ✅ **Comando `/adicionar_estoque` Reformulado** - Melhorado (22/10/2025)
  - Agora é um **comando slash** completo
  - Interface com **Select Menu** para escolher produto
  - Sistema de mensagens (sem Modal, mais compatível)
  - Deleta códigos automaticamente por segurança
  - Filtra apenas produtos que precisam de estoque gerenciado

- ✅ **Pagamento Automático Corrigido** - Bugs resolvidos (22/10/2025)
  - QR Code agora envia como **imagem PNG** automaticamente
  - Correção de erros de `guild_id` no ticket_manager
  - Sistema de verificação a cada 2 minutos funcionando perfeitamente
  - Entrega instantânea após confirmação do pagamento

- ✅ **Sistema de Suporte com Select Menu** - `/setup_suporte` reformulado (21/10/2025)
  - Interface ultra profissional com **UM botão + dropdown menu**
  - Suporta até **25 categorias** diferentes (vs 5 botões antes)
  - Usuário clica no botão → Abre menu → Seleciona categoria
  - Botão principal customizável (Nome | Emoji)
  - UI muito mais limpa e organizada
  - Formato das opções: `EMOJI|Nome|Descrição` (um por linha)

- ✅ **Sistema de Cupons** - Sistema completo implementado (21/10/2025)
  - Cupons com desconto percentual
  - Limite de uso e restrição por usuário
  - Split de pagamento para parcerias
  - Estatísticas e rastreamento completo
  - Comandos: `/criar_cupom`, `/listar_cupons`, `/cupom_stats`, `/deletar_cupom`

### **Comandos Principais para Lembrar:**
```bash
# Iniciar o bot
python bot.py

# Comandos no Discord (Admin) - Multi-Servidor
/admin_criar_produto     # Criar produto no servidor (atualiza Supabase diretamente)
/admin_criar_vip         # Criar produto VIP (estoque ilimitado automático)
/admin_listar_produtos   # Ver todos produtos do servidor
/admin_deletar_produto   # Deletar múltiplos produtos (ex: 1,2,3)
/adicionar_estoque       # Adicionar códigos/keys (apenas produtos gerenciados)

# Comandos no Discord (Admin) - Geral
/setup_ticket          # Configurar sistema de tickets de compra
/setup_suporte         # Configurar sistema de tickets de suporte
/close_ticket          # Fechar ticket manualmente

# Comandos no Discord (Usuário)
/produtos              # Ver produtos disponíveis do servidor
/comprar               # Comprar produto (dentro do ticket)
/status                # Ver status do pagamento
/ajuda                 # Ver lista completa de comandos
```

---

## 🚀 Funcionalidades

### 🎫 Sistema de Tickets
- **Criação via Botão**: Admin envia mensagem com botão "Criar Ticket de Compra"
- **Modal de Seleção**: Usuário escolhe produto em modal interativo
- **Canais Privados**: Criação automática de canais privados para cada ticket
- **Fechamento Automático**: Tickets fecham após pagamento aprovado ou manualmente por admin

### 💳 Sistema de Pagamento
- **Pagamento via Pix**: Geração automática de QR Code e código Pix
- **Sem Email Obrigatório**: Usa email padrão baseado no nome do usuário
- **Monitoramento Automático**: Verificação automática do status do pagamento
- **Entrega Instantânea**: Entrega automática após confirmação

### 🤖 Comandos Modernos
- **Slash Commands**: Comandos com `/` para melhor experiência
- **Compatibilidade**: Mantém comandos com `!` para compatibilidade
- **Interface Intuitiva**: Botões, modals e embeds interativos

## 🛠️ Tecnologias

- **Linguagem**: Python 3.8+
- **Discord API**: py-cord
- **Banco de Dados**: Supabase (PostgreSQL)
- **Pagamento via Pix**: PushinPay API
- **QR Code**: qrcode library

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no Discord (para criar o bot)
- Conta no Supabase (para o banco de dados)
- Conta na PushinPay (para pagamentos via Pix)

## 🔧 Instalação

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd CaosBot-Discord
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**:
   - Copie o arquivo `env.example` para `.env`
   - Preencha as configurações necessárias:
   ```env
   DISCORD_TOKEN=seu_token_do_discord
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_chave_do_supabase
   PUSHINPAY_API_KEY=sua_chave_da_pushinpay
   ```

## ⚙️ Configuração

### 1. Criar arquivo .env
Execute: `python criar_env.py` ou crie manualmente:

```env
# Discord
DISCORD_TOKEN=842c8e29352ebd03e85b29f8c1c4ed6ee2e981194ad0236c153e3bb234c3848f
DISCORD_APPLICATION_ID=784058182515425310

# Supabase
SUPABASE_URL=https://sxsaxcqliuiolktypwkf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4c2F4Y3FsaXVpb2xrdHlwd2tmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NTQwNDksImV4cCI6MjA3NjQzMDA0OX0.Qc-DINC-FC9oPbI4BBpxbtF9OmTMUN8ecC1gDSTatbY

# PushinPay
PUSHINPAY_API_KEY=50790|dakuggRtFoHjIZb2XpYYbDoa2exlT5NPspJayboI40bfb10f
PUSHINPAY_SANDBOX=true

# Configurações do Bot
BOT_PREFIX=?
```

### 2. Configurar Supabase - PASSO A PASSO COMPLETO

#### **2.1 - Criar Projeto no Supabase**
1. Acesse: https://supabase.com
2. Clique em **"New Project"**
3. Preencha:
   - **Name**: CaosBot (ou qualquer nome)
   - **Database Password**: Escolha uma senha forte
   - **Region**: South America (São Paulo)
4. Aguarde ~2 minutos para criar

#### **2.2 - Copiar Credenciais**
1. Vá em **Settings** → **API**
2. Copie:
   - **URL**: Sua URL do projeto
   - **anon/public key**: Sua chave API

#### **2.3 - Executar SQL no Banco de Dados**

**IMPORTANTE:** Execute os SQLs na ordem abaixo. Vá em **SQL Editor** → **New query** e execute cada bloco:

**PASSO 1 - Execute o arquivo `database_coupon_setup.sql`**
```bash
# Abra o arquivo database_coupon_setup.sql e cole todo conteúdo no SQL Editor
# Isso criará: tabelas de cupons, produtos, transações e funções
```

**PASSO 2 - Execute o arquivo `database_vip_setup.sql`**
```bash
# Abra o arquivo database_vip_setup.sql e cole todo conteúdo no SQL Editor
# Isso criará: tabela de assinaturas VIP e triggers
```

**PASSO 2.5 - Execute o arquivo `database_multiserver_setup_v2.sql`**
```bash
# Abra o arquivo database_multiserver_setup_v2.sql e cole todo conteúdo no SQL Editor
# Isso criará: guild_config, guild_id nas tabelas, e sistema multi-servidor
```

**PASSO 2.6 - Execute o arquivo `database_unlimited_stock.sql`**
```bash
# Abra o arquivo database_unlimited_stock.sql e cole todo conteúdo no SQL Editor
# Isso adicionará: campo unlimited_stock para produtos com estoque infinito
```

**PASSO 3 - DESABILITAR RLS (Row Level Security) - ESSENCIAL!**
```sql
-- Execute este SQL para permitir que o bot acesse as tabelas
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE coupons DISABLE ROW LEVEL SECURITY;
ALTER TABLE coupon_usage DISABLE ROW LEVEL SECURITY;
ALTER TABLE vip_subscriptions DISABLE ROW LEVEL SECURITY;
ALTER TABLE guild_config DISABLE ROW LEVEL SECURITY;
ALTER TABLE product_inventory DISABLE ROW LEVEL SECURITY;
```

**PASSO 4 - Verificar se funcionou**
```sql
-- Ver todas as tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Deve mostrar: coupons, coupon_usage, products, transactions, vip_subscriptions
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Sistema de Tickets (Opcional)
Adicione estas variáveis ao `.env` para configurar o sistema de tickets:

```env
# Configurações de Tickets (Opcional)
TICKET_CATEGORY_ID=1234567890123456789  # ID da categoria para tickets
ADMIN_ROLE_ID=1234567890123456789       # ID do role de admin
TICKET_LOGS_CHANNEL_ID=1234567890123456789  # ID do canal para logs
```

**Como obter os IDs:**
- **Categoria**: Clique com botão direito na categoria > "Copiar ID"
- **Role**: Clique com botão direito no role > "Copiar ID"  
- **Canal**: Clique com botão direito no canal > "Copiar ID"

### 5. Convidar Bot para Servidor
1. Acesse: https://discord.com/developers/applications/784058182515425310
2. Vá para "OAuth2" > "URL Generator"
3. Selecione "bot" e "Send Messages"
4. Copie a URL e abra no navegador


## 🎮 Comandos do Bot

### 🎫 Sistema de Tickets
1. **Admin**: Use `/setup_ticket` para enviar mensagem com botão
2. **Usuário**: Clique em "Criar Ticket de Compra"
3. **Modal**: Escolha o produto desejado
4. **Canal**: Acesse seu canal privado para continuar

### 📱 Comandos Slash (Recomendado)
- `/ajuda` - Lista de comandos e instruções
- `/produtos` - Ver produtos disponíveis
- `/comprar` - ✨ **Gerar pagamento automaticamente** (detecta produto do ticket!)
- `/status` - Verificar status do pagamento
- `/setup_ticket` - [ADMIN] Enviar mensagem de tickets de compra
- `/setup_suporte` - [ADMIN] Enviar mensagem de tickets de suporte customizados
- `/close_ticket` - [ADMIN] Fechar ticket manualmente

### 🔧 Comandos Legacy (!)
- `!products` - Ver produtos disponíveis
- `!buy <produto>` - Comprar produto (no canal do ticket)
- `!status` - Status do pagamento
- `!ajuda` - Lista de comandos (compatibilidade)

## 🎯 Como Usar o Sistema de Tickets

### Para Administradores:
1. **Configurar Sistema**: Use `/setup_ticket` no canal onde quer que apareça o botão
2. **Gerenciar Tickets**: Use `/close_ticket` em qualquer canal de ticket para fechá-lo
3. **Monitorar Logs**: Configure `TICKET_LOGS_CHANNEL_ID` para receber logs de criação/fechamento

### Para Usuários:
1. **Criar Ticket**: Clique no botão "Criar Ticket de Compra" na mensagem do bot
2. **Escolher Produto**: Selecione o produto desejado no modal que aparece
3. **Acessar Canal**: Vá para o canal privado criado automaticamente
4. **Pagamento Automático**: O bot gera o pagamento automaticamente
5. **Ou Manual**: Se falhar, use `/comprar` (detecta o produto automaticamente!)
6. **Acompanhar**: Use `/status` para verificar o progresso do pagamento

### Fluxo Completo:
```
Admin → /setup_ticket → Botão aparece
Usuário → Clica botão → Modal com produtos
Usuário → Escolhe produto → Canal privado criado
Bot → Pagamento gerado AUTOMATICAMENTE com QR Code
Se falhar → Usuário digita /comprar → Pagamento gerado
Usuário → Paga → Bot detecta → Entrega automática
```

**✨ Melhorias de UX:**
- ✅ Pagamento automático ao criar ticket
- ✅ Comando `/comprar` **sem parâmetros** - detecta produto automaticamente
- ✅ Mensagens claras e instruções diretas
- ✅ Logs detalhados para troubleshooting

## 🆘 Sistema de Suporte Customizado

O comando `/setup_suporte` permite criar um painel de atendimento super profissional com **um botão + menu dropdown** contendo até **25 opções diferentes**!

### Como Funciona:

1. **Admin executa** `/setup_suporte`
2. **Bot cria** uma mensagem com UM botão
3. **Usuário clica** no botão
4. **Abre um menu dropdown** com todas as opções de atendimento
5. **Usuário seleciona** a categoria (ex: Parcerias, Dúvidas, etc)
6. **Ticket é criado** com a categoria escolhida!

### Como Configurar:

1. **Execute o comando** `/setup_suporte` no canal desejado
2. **Preencha o modal** com as informações:
   - **Título**: Nome da mensagem embed (ex: "Central de Atendimento")
   - **Descrição**: Texto explicativo abaixo do título
   - **Opções Menu**: Categorias do dropdown no formato `EMOJI|Nome|Descrição`
   - **Nome do Botão | Emoji**: Customização do botão principal (ex: "Abrir Ticket | 🎫")
   - **Cor**: Código hexadecimal do embed (ex: #5865F2)

### Formato das Opções:
```
EMOJI|Nome|Descrição
```

### Exemplo Completo:
```
❤️|Parcerias|Para os interessados em colaborar conosco.
💡|Dúvidas|Caso esteja com dúvidas em algo, abra um ticket.
✅|Denúncias|Realize denúncias através desse ticket.
🎁|Sorteios|Aqui você poderá resgatar sua premiação de sorteios.
```

### Formato do Botão:
```
Nome | Emoji
```
Exemplo: `Abrir Ticket | 🎫` ou `Suporte | 💬`

### O que acontece:
- ✅ **Interface limpa**: Apenas UM botão na mensagem
- ✅ **Menu dropdown**: Ao clicar, abre menu com todas as opções
- ✅ **Categorizado**: Cada opção cria um ticket com categoria específica
- ✅ **Nome do canal**: Inclui a categoria (ex: `parcerias-usuario-1021`)
- ✅ **Mensagem personalizada**: Boas-vindas com emoji e nome da categoria
- ✅ **Limite**: Apenas um ticket ativo por usuário (qualquer tipo)

### Vantagens do Select Menu:
- 🎯 **UI Profissional**: Interface muito mais limpa que múltiplos botões
- 📊 **Escalável**: Até 25 opções diferentes (vs 5 botões máximo)
- 🎨 **Organizado**: Todas as opções em um único menu
- ⚡ **Rápido**: Usuário encontra a opção facilmente

### Diferença entre `/setup_ticket` e `/setup_suporte`:
- **`/setup_ticket`**: Para vendas - usuário escolhe produto e pode comprar
- **`/setup_suporte`**: Para atendimento - menu de categorias, tickets sem venda

## 🏗️ Estrutura do Projeto

```
/bot_project
├── bot.py                    # Arquivo principal do bot
├── commands/                 # Comandos específicos do bot
│   ├── __init__.py
│   ├── product_commands.py   # Comandos relacionados aos produtos
│   └── payment_commands.py   # Comandos relacionados ao pagamento
├── models/                   # Modelos de dados e interações com o banco
│   ├── __init__.py
│   ├── product_model.py      # Interações com os produtos no banco
│   └── transaction_model.py  # Interações com as transações no banco
├── utils/                    # Funções utilitárias
│   ├── __init__.py
│   ├── payment_utils.py      # Funções para gerar cobrança via Pix
│   ├── ticket_views.py       # Views e Modals do Discord para tickets
│   └── ticket_manager.py     # Gerenciador de canais de ticket
├── config/                   # Arquivos de configuração
│   ├── __init__.py
│   └── config.py            # Configurações do bot
├── data/                     # Armazenamento de dados
│   └── .gitkeep
├── requirements.txt          # Dependências do projeto
├── env.example              # Exemplo de configuração
├── criar_env.py             # Script para criar arquivo .env
└── README.md                # Documentação
```

**Importante**: Mantenha sempre a estrutura organizada. Cada funcionalidade deve ser colocada em sua pasta específica. O arquivo principal é o `bot.py` - todos os ajustes e novas funcionalidades devem ser feitos diretamente neste arquivo ou em módulos importados. **Não crie arquivos de teste ou experimentais fora da estrutura de pastas organizada.**

## 🚀 Executando o Bot

### Para Testes Locais:
```bash
python bot.py
```

### Para Produção (Deploy):
O bot precisa rodar 24/7 para funcionar no Discord. Use uma das opções:

#### 1. Shard Cloud (Recomendado - Gratuito):
1. Entre na comunidade Discord da Shard Cloud para obter plano gratuito
2. Acesse: https://shardcloud.app
3. Crie repositório no GitHub com o código do bot
4. "New Project" → Conecte GitHub
5. Selecione seu repositório
6. Configure variáveis de ambiente:
   ```
   DISCORD_TOKEN=842c8e29352ebd03e85b29f8c1c4ed6ee2e981194ad0236c153e3bb234c3848f
   DISCORD_APPLICATION_ID=784058182515425310
   SUPABASE_URL=https://sxsaxcqliuiolktypwkf.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4c2F4Y3FsaXVpb2xrdHlwd2tmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NTQwNDksImV4cCI6MjA3NjQzMDA0OX0.Qc-DINC-FC9oPbI4BBpxbtF9OmTMUN8ecC1gDSTatbY
   PUSHINPAY_API_KEY=50790|dakuggRtFoHjIZb2XpYYbDoa2exlT5NPspJayboI40bfb10f
   PUSHINPAY_SANDBOX=true
   ```
7. Deploy automático

#### 2. Railway (Alternativa):
1. Acesse: https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Configure variáveis de ambiente
4. Deploy

#### 3. VPS Próprio:
```bash
pm2 start bot.py --name discord-bot
pm2 save
pm2 startup
```

### Vantagens da Shard Cloud:
- ✅ **Plano gratuito** disponível via comunidade Discord
- ✅ **2GB RAM, 2 vCPU** no plano gratuito
- ✅ **Deploy via GitHub** automático
- ✅ **Auto Restart** para manter bot online
- ✅ **Suporte à comunidade** no Discord
- ✅ **Infraestrutura rápida** e confiável

**IMPORTANTE**: NUNCA crie arquivos de guia separados. Sempre inclua instruções diretas no README para não esquecer.

**🚨 DEPLOY OBRIGATÓRIO**: SEMPRE use a **Shard Cloud** para deploy. NUNCA use Vercel, Railway ou outras plataformas. A Shard Cloud é a plataforma oficial e recomendada para este projeto.

## 🚀 Como Fazer Deploy na Shard Cloud

### **Passo a Passo Completo:**

#### **1. Preparação do Código (Git)**
```bash
# Fazer mudanças no código
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

#### **2. Deploy na Shard Cloud**
1. **Acesse**: https://shardcloud.app
2. **Faça login** com sua conta
3. **"New Project"** → Conecte GitHub
4. **Selecione**: `idkafael/Khaos`
5. **Configure variáveis de ambiente**:
   ```
   DISCORD_TOKEN=842c8e29352ebd03e85b29f8c1c4ed6ee2e981194ad0236c153e3bb234c3848f
   DISCORD_APPLICATION_ID=784058182515425310
   SUPABASE_URL=https://sxsaxcqliuiolktypwkf.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4c2F4Y3FsaXVpb2xrdHlwd2tmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NTQwNDksImV4cCI6MjA3NjQzMDA0OX0.Qc-DINC-FC9oPbI4BBpxbtF9OmTMUN8ecC1gDSTatbY
   PUSHINPAY_API_KEY=50790|dakuggRtFoHjIZb2XpYYbDoa2exlT5NPspJayboI40bfb10f
   PUSHINPAY_SANDBOX=true
   ```
6. **Deploy automático** será iniciado

#### **3. Deploy Automático (Após Configuração Inicial)**
Após a configuração inicial, os deploys são automáticos:
```bash
# Qualquer commit + push triggera deploy automático
git commit --allow-empty -m "🚀 Deploy de teste"
git push origin main
```

### **📋 Checklist de Deploy:**
- ✅ Código commitado e enviado para GitHub
- ✅ Variáveis de ambiente configuradas na Shard Cloud
- ✅ Projeto conectado ao repositório GitHub
- ✅ Deploy automático funcionando
- ✅ Bot online e respondendo

### **🔧 Comandos Úteis:**
```bash
# Deploy forçado (commit vazio)
git commit --allow-empty -m "🚀 Deploy forçado"
git push origin main

# Verificar status do repositório
git status
git log --oneline -5
```

**IMPORTANTE**: O deploy é sempre automático após push para GitHub. Não é necessário fazer nada manual na Shard Cloud após a configuração inicial.

---

## ✅ CHECKLIST COMPLETO DE DEPLOY

Use este checklist para garantir que tudo está configurado corretamente:

### 📋 Pré-Deploy (Local)

- [ ] Arquivo `.env` criado com todas as variáveis
- [ ] `BOT_PREFIX` configurado como `?` no `.env`
- [ ] Supabase configurado (credenciais no `.env`)
- [ ] SQL executado no Supabase (`database_coupon_setup.sql`)
- [ ] SQL executado no Supabase (`database_vip_setup.sql`)
- [ ] RLS desabilitado nas 5 tabelas do Supabase
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Bot testado localmente (`python bot.py`)

### 🚀 Deploy na Shard Cloud

- [ ] Código commitado e enviado para GitHub
- [ ] Projeto criado/conectado na Shard Cloud
- [ ] Variáveis de ambiente configuradas:
  - [ ] `DISCORD_TOKEN`
  - [ ] `DISCORD_APPLICATION_ID`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `PUSHINPAY_API_KEY`
  - [ ] `PUSHINPAY_SANDBOX` = `true`
  - [ ] `BOT_PREFIX` = `?`
  - [ ] `LOG_LEVEL` = `INFO` (opcional)
  - [ ] `ENVIRONMENT` = `production` (opcional)
- [ ] Deploy concluído com sucesso
- [ ] Bot aparece online no Discord

### 🎮 Pós-Deploy

- [ ] Bot convidado para o servidor Discord
- [ ] Comando `/teste` funcionando
- [ ] Sistema de tickets configurado (`/setup_ticket`)
- [ ] Produtos VIP cadastrados no banco
- [ ] Cupons de desconto criados
- [ ] Testado fluxo completo de compra

### 🆘 Troubleshooting

**Bot não conecta?**
- Verifique `DISCORD_TOKEN` nas variáveis de ambiente
- Veja os logs na Shard Cloud

**Erro de banco de dados?**
- Verifique `SUPABASE_URL` e `SUPABASE_KEY`
- Confirme que as tabelas foram criadas
- Verifique se RLS foi desabilitado

**Comandos não aparecem?**
- Aguarde até 1 hora (cache do Discord)
- Ou retire e convide o bot novamente

---

## 📊 Produtos de Exemplo

O bot vem com 8 produtos digitais pré-configurados:

### 🎮 Jogos Digitais
1. **Minecraft Premium** - R$ 45,00
   - Conta Minecraft Premium original com acesso completo ao jogo. Inclui skin personalizada e histórico limpo.

### 📺 Streaming
2. **Spotify Premium** - R$ 25,00
   - Conta Spotify Premium válida por 3 meses. Música sem anúncios, download offline e qualidade máxima.

3. **Netflix Premium** - R$ 35,00
   - Conta Netflix Premium compartilhada por 1 mês. Acesso completo a todos os conteúdos em 4K.

4. **YouTube Premium** - R$ 30,00
   - YouTube Premium por 3 meses. Sem anúncios, downloads offline e YouTube Music incluído.

### 🎯 Gaming
5. **Discord Nitro** - R$ 20,00
   - Discord Nitro válido por 1 mês. Uploads maiores, emojis personalizados e boost de servidor.

6. **Steam Wallet** - R$ 50,00
   - Saldo Steam Wallet de R$ 50,00. Use para comprar jogos, DLCs e itens na Steam.

### 💻 Software
7. **Adobe Creative Cloud** - R$ 80,00
   - Acesso completo ao Adobe Creative Cloud por 1 mês. Photoshop, Illustrator, Premiere Pro e mais.

8. **Office 365** - R$ 60,00
   - Microsoft Office 365 válido por 1 ano. Word, Excel, PowerPoint e OneDrive com 1TB.

## 🔄 Fluxo do Bot

1. **Criação de Ticket**:
   - Usuário envia `!start`
   - Bot cria canal privado para o ticket
   - Envia mensagem de boas-vindas

2. **Escolha do Produto**:
   - Usuário envia `!products` para ver produtos
   - Usuário envia `!buy <produto>` para escolher

3. **Geração de Cobrança via Pix**:
   - Bot solicita email do usuário
   - Utiliza API OpenPix para gerar cobrança
   - Envia QR Code e código Pix

4. **Acompanhamento do Pagamento**:
   - Bot monitora status via OpenPix
   - Atualiza banco de dados automaticamente

5. **Entrega do Produto**:
   - Bot confirma pagamento
   - Entrega produto digitalmente
   - Notifica usuário

## 🛡️ Segurança

- Todas as transações são validadas
- Emails são validados antes do processamento
- Tokens e chaves são armazenados em variáveis de ambiente
- Logs de todas as operações importantes

## 🐛 Solução de Problemas

### ⚠️ Pagamento Automático Falhou

**Sintoma:** Ao criar ticket, aparece mensagem "Pagamento Automático Falhou"

**Causas Comuns:**
1. **Produto sem estoque** - Adicione estoque usando `/adicionar_estoque`
2. **Erro na API PushinPay** - Verifique se a API Key está correta no `.env`
3. **Produto VIP sem `unlimited_stock`** - Execute o SQL: `database_unlimited_stock.sql`
4. **Guild ID ausente** - Execute o SQL: `database_multiserver_setup_v2.sql`

**Solução Rápida:**
```bash
# Usuário pode usar comando manual
/comprar produto: Nome do Produto
```

**Verificar Logs:**
```bash
# Procure por estas mensagens no console:
🔄 Gerando pagamento automático...
❌ Falha ao criar transação no banco de dados
❌ Falha ao gerar pagamento Pix
```

**Correção Permanente:**
- ✅ Execute `database_unlimited_stock.sql` no Supabase
- ✅ Verifique `PUSHINPAY_API_KEY` no `.env`
- ✅ Adicione estoque para produtos gerenciados
- ✅ Reinicie o bot

📄 **Documentação completa:** Veja `FIX_PAGAMENTO_AUTOMATICO.md`

---

### Erro de Conexão com Supabase
- Verifique se as credenciais estão corretas
- Confirme se as tabelas foram criadas
- Verifique se o projeto está ativo

### Erro de Pagamento PushinPay
- Verifique se a API Key está correta no `.env`
- Confirme se está usando modo PRODUÇÃO (não sandbox)
- Verifique os logs para mais detalhes
- Consulte: https://pushinpay.com.br/docs

### Bot não responde
- Verifique se o token do Discord está correto
- Confirme se as intents estão habilitadas
- Verifique se o bot tem permissões no servidor

## 📝 Logs

O bot gera logs detalhados em:
- Console (desenvolvimento)
- Arquivo `bot.log` (produção)

Níveis de log configuráveis via variável `LOG_LEVEL`.

## 🗄️ Estrutura do Banco de Dados

### Tabela: product_inventory

Esta tabela gerencia o estoque de produtos digitais (códigos, keys, contas, etc).

```sql
CREATE TABLE product_inventory (
  id SERIAL PRIMARY KEY,
  product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'reserved', 'sold', 'expired')),
  sold_to_user_id BIGINT,
  reserved_at TIMESTAMP,
  sold_at TIMESTAMP,
  transaction_id INTEGER REFERENCES transactions(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_product_inventory_product_id ON product_inventory(product_id);
CREATE INDEX idx_product_inventory_status ON product_inventory(status);
CREATE INDEX idx_product_inventory_transaction_id ON product_inventory(transaction_id);
```

### Campos Adicionais na Tabela transactions

Adicione estes campos à tabela `transactions` existente:

```sql
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS inventory_id INTEGER REFERENCES product_inventory(id);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS delivery_channel_id BIGINT;
```

### Fluxo de Estoque

1. **Disponível** (`available`): Item pronto para venda
2. **Reservado** (`reserved`): Item reservado durante pagamento (até 10min)
3. **Vendido** (`sold`): Item entregue ao cliente
4. **Expirado** (`expired`): Reserva expirou, volta para disponível

### Como Adicionar Produtos ao Estoque

Use o comando `/adicionar_estoque` no Discord (requer permissão de admin):

1. Execute `/adicionar_estoque`
2. Selecione o produto
3. Cole os códigos/keys (um por linha)
4. Confirme

Exemplo de códigos:
```
MINECRAFT-XXXX-YYYY-ZZZZ
NETFLIX-EMAIL:SENHA
SPOTIFY-KEY-12345
```

## 🎟️ Sistema de Cupons de Desconto

Sistema completo de cupons com descontos percentuais, limites de uso, split de pagamento e estatísticas detalhadas.

### Funcionalidades

- ✅ **Descontos Percentuais** - De 1% até 100%
- ✅ **Limite de Usos** - Controle total ou ilimitado
- ✅ **Um Uso por Usuário** - Evita abuso de cupons
- ✅ **Split de Pagamento** - Integrado com PushinPay para parcerias
- ✅ **Data de Expiração** - Cupons com validade
- ✅ **Estatísticas Completas** - Rastreamento de uso e revenue
- ✅ **Aplicação Automática** - Cupom aplicado ao criar ticket

### Estrutura do Banco de Dados

Execute o arquivo `database_coupon_setup.sql` no Supabase SQL Editor ou execute manualmente:

```sql
-- Tabela de cupons
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent DECIMAL(5,2) NOT NULL,
    max_uses INTEGER DEFAULT NULL,
    uses_count INTEGER DEFAULT 0,
    one_per_user BOOLEAN DEFAULT false,
    split_enabled BOOLEAN DEFAULT false,
    split_recipient_id VARCHAR(255),
    split_percent DECIMAL(5,2),
    expires_at TIMESTAMP,
    active BOOLEAN DEFAULT true,
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de uso de cupons
CREATE TABLE coupon_usage (
    id SERIAL PRIMARY KEY,
    coupon_id INTEGER REFERENCES coupons(id),
    user_id BIGINT NOT NULL,
    transaction_id INTEGER REFERENCES transactions(id),
    discount_amount DECIMAL(10,2),
    used_at TIMESTAMP DEFAULT NOW()
);

-- Atualizar tabela transactions
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS coupon_id INTEGER REFERENCES coupons(id),
ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS final_amount DECIMAL(10,2);

-- Função para incrementar contador
CREATE OR REPLACE FUNCTION increment_coupon_uses(coupon_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE coupons 
    SET uses_count = uses_count + 1,
        updated_at = NOW()
    WHERE id = coupon_id;
END;
$$ LANGUAGE plpgsql;
```

### Comandos Administrativos

#### `/criar_cupom`
Cria um novo cupom via modal interativo.

**Campos:**
- Código do cupom (uppercase automático)
- Desconto % (1-100)
- Limite de usos (0 = ilimitado)
- Um uso por usuário (sim/não)
- Data de expiração (DD/MM/YYYY, opcional)

**Exemplo:**
```
/criar_cupom
> Código: PRIMEIRACOMPRA
> Desconto: 15
> Limite: 0
> Um por usuário: sim
> Expiração: 31/12/2025
```

#### `/listar_cupons`
Lista todos os cupons ativos com informações resumidas.

**Exibe:**
- Código do cupom
- Percentual de desconto
- Usos atuais / limite
- Restrição por usuário
- Data de expiração

#### `/cupom_stats [codigo]`
Estatísticas detalhadas de um cupom específico.

**Mostra:**
- Total de usos
- Desconto total aplicado
- Últimos usuários que usaram
- Limite e status
- Data de expiração

**Exemplo:**
```
/cupom_stats CAOS
```

#### `/deletar_cupom [codigo]`
Desativa um cupom (não deleta do banco, apenas marca como inativo).

**Exemplo:**
```
/deletar_cupom VIP10
```

### Como Usar (Para Clientes)

1. Ao criar ticket, aparece modal para escolher produto
2. Após escolher produto, aparece campo opcional para cupom
3. Digite o código do cupom (ex: PRIMEIRACOMPRA)
4. Cupom é validado automaticamente
5. Desconto é aplicado no pagamento Pix

**Validações Automáticas:**
- ✅ Cupom existe e está ativo
- ✅ Não expirou
- ✅ Não atingiu limite de usos
- ✅ Usuário não usou antes (se configurado)

### Split de Pagamento (Parcerias)

Cupons podem ter split configurado para parcerias:

**Exemplo de Uso:**
```
Cupom: PARCEIRO30
Desconto: 30%
Split: 70% você / 30% parceiro
```

Quando cliente usa este cupom:
- Recebe 30% de desconto
- Do valor pago, 30% vai para o parceiro
- Split é processado automaticamente pela PushinPay

**Configurar Split:**
Edite o cupom no banco de dados:
```sql
UPDATE coupons SET
    split_enabled = true,
    split_recipient_id = 'recipient_id_pushinpay',
    split_percent = 30
WHERE code = 'PARCEIRO30';
```

### Estatísticas e Rastreamento

Todos os usos de cupons são rastreados:

```sql
-- Ver todos os usos de um cupom
SELECT cu.*, t.amount, t.final_amount
FROM coupon_usage cu
JOIN transactions t ON t.id = cu.transaction_id
WHERE cu.coupon_id = (SELECT id FROM coupons WHERE code = 'CAOS');

-- Revenue total com descontos
SELECT 
    c.code,
    COUNT(cu.id) as total_uses,
    SUM(cu.discount_amount) as total_discount,
    SUM(t.final_amount) as total_revenue
FROM coupons c
LEFT JOIN coupon_usage cu ON cu.coupon_id = c.id
LEFT JOIN transactions t ON t.id = cu.transaction_id
WHERE t.status = 'approved'
GROUP BY c.code;
```

### Exemplos de Cupons

```sql
-- Cupom de primeira compra (15% off, um por usuário)
INSERT INTO coupons (code, discount_percent, one_per_user) 
VALUES ('PRIMEIRACOMPRA', 15, true);

-- Cupom de parceria (30% off, split 30% para parceiro)
INSERT INTO coupons (code, discount_percent, split_enabled, split_recipient_id, split_percent) 
VALUES ('PARCEIRO30', 30, true, 'rec_abc123', 30);

-- Cupom limitado (10% off, máximo 100 usos)
INSERT INTO coupons (code, discount_percent, max_uses) 
VALUES ('PROMO10', 10, 100);

-- Cupom com expiração
INSERT INTO coupons (code, discount_percent, expires_at) 
VALUES ('NATAL25', 25, '2025-12-31 23:59:59');
```

### Fluxo Completo

```
1. Cliente clica "Criar Ticket"
2. Escolhe produto no select menu
3. Modal pede cupom (opcional)
4. Cliente digita "PRIMEIRACOMPRA"
5. Ticket criado com cupom vinculado
6. Ao usar /comprar:
   - Cupom validado
   - Desconto calculado (15%)
   - Pix gerado com valor final
   - Uso registrado
   - Split processado (se configurado)
7. Estatísticas atualizadas automaticamente
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais informações.

## 📞 Suporte

Se você encontrar algum problema ou tiver sugestões:

1. Abra uma [issue](https://github.com/seu-usuario/CaosBot-Discord/issues)
2. Entre em contato via Discord
3. Consulte a documentação da [OpenPix](https://docs.openpix.com.br)
4. Consulte a documentação do [Supabase](https://supabase.com/docs)

## 👑 Sistema VIP - Gerenciamento de Assinaturas

Sistema completo de gerenciamento de assinaturas VIP no Discord com roles temporárias, controle automático de expiração e notificações via DM.

### Visão Geral

O Sistema VIP permite vender e gerenciar acesso premium no Discord com:
- ✅ **Roles automáticas** - Adicionadas após pagamento
- ✅ **Duração flexível** - 1 dia, 15 dias, 30 dias ou vitalício
- ✅ **Expiração automática** - Remove roles automaticamente
- ✅ **Notificações DM** - Boas-vindas, avisos e expiração
- ✅ **Cores personalizadas** - Roles com cores predefinidas
- ✅ **Gestão completa** - Comandos para usuários e admins

### Produtos VIP Disponíveis

- **VIP Bronze - 1 Dia** - R$ 5,00
- **VIP Bronze - 15 Dias** - R$ 25,00
- **VIP Bronze - 30 Dias** - R$ 45,00
- **VIP Prata - 30 Dias** - R$ 75,00
- **VIP Ouro - 30 Dias** - R$ 120,00
- **VIP Diamante - Vitalício** - R$ 500,00

### Instalação Rápida

1. **Execute o SQL no Supabase:**
```bash
# Cole o conteúdo de database_vip_setup.sql no SQL Editor
```

2. **Configure permissões do bot:**
   - Manage Roles (Gerenciar Cargos)
   - Bot deve estar ACIMA das roles VIP na hierarquia

3. **Reinicie o bot:**
```bash
python bot.py
```

### Comandos de Usuário

```bash
/meu_vip         # Ver status da assinatura VIP
/renovar_vip     # Ver planos disponíveis
/historico_vip   # Ver histórico de assinaturas
```

### Comandos Admin

```bash
/listar_vips                              # Listar VIPs ativos
/adicionar_vip @user "Role VIP" [dias]    # Adicionar VIP manual
/remover_vip @user                        # Remover VIP
/vip_stats                                # Estatísticas
```

### Fluxo de Compra VIP

```
Cliente → Abre Ticket → Escolhe VIP → Paga via Pix
  → Role Adicionada Automaticamente → DM de Boas-vindas
  → Expiração Automática após X dias
```

### Sistema Automático

O bot verifica **a cada 6 horas**:
- ✅ Expira assinaturas vencidas
- ✅ Remove roles expiradas
- ✅ Envia avisos 3 dias antes da expiração
- ✅ Envia notificação ao expirar

### Notificações DM

1. **Boas-vindas** - Ao ativar VIP
2. **Aviso** - 3 dias antes de expirar
3. **Expiração** - Quando VIP expira

### Documentação SQL

- **Estrutura SQL:** `database_vip_setup.sql` - Execute no Supabase para criar tabelas VIP

### Estrutura do Banco

Execute `database_vip_setup.sql` para criar:
- Tabela `vip_subscriptions`
- Campo `vip_config` em `products`
- Índices otimizados
- Triggers automáticos

### Cores das Roles VIP

| Role | Cor | RGB |
|------|-----|-----|
| VIP Bronze | 🟤 | 205, 127, 50 |
| VIP Prata | ⚪ | 192, 192, 192 |
| VIP Ouro | 🟡 | 255, 215, 0 |
| VIP Diamante | 💎 | 185, 242, 255 |

### Troubleshooting

**Role não foi adicionada?**
- Verificar hierarquia (bot acima das roles VIP)
- Verificar permissão "Manage Roles"

**DM não foi enviada?**
- Normal se usuário tiver DMs desabilitadas
- Sistema funciona mesmo sem DM

**VIP não expirou?**
- Task roda a cada 6 horas
- Pode ter delay de até 6h

---

## 🎯 Como Criar e Gerenciar Produtos VIP

### 📝 Estrutura de um Produto VIP

Os produtos VIP são cadastrados na tabela `products` com um campo JSON `vip_config`:

```sql
INSERT INTO products (name, description, price, category, vip_config) VALUES
(
  'Nome do Produto',                        -- Ex: "VIP Premium - 30 Dias"
  'Descrição do produto',                   -- Descrição detalhada
  49.90,                                    -- Preço em R$
  'vip',                                    -- SEMPRE 'vip' para produtos VIP
  '{"role_name": "Nome da Role", "duration_days": 30}'::jsonb  -- Configuração VIP
);
```

### 🆕 Criar Novos Produtos VIP

**1. VIP Temporário (30 dias):**
```sql
INSERT INTO products (name, description, price, category, vip_config) VALUES
('VIP Premium - 30 Dias', 'Acesso VIP Premium por 30 dias', 49.90, 'vip',
 '{"role_name": "VIP Premium", "duration_days": 30}'::jsonb);
```

**2. VIP Vitalício (NUNCA EXPIRA):**
```sql
INSERT INTO products (name, description, price, category, vip_config) VALUES
('VIP Ultimate - Vitalício', 'Acesso VIP permanente!', 299.90, 'vip',
 '{"role_name": "VIP Ultimate", "duration_days": null}'::jsonb);
```

**3. VIP Semanal:**
```sql
INSERT INTO products (name, description, price, category, vip_config) VALUES
('VIP Trial - 7 Dias', 'Teste nosso VIP por 7 dias', 15.00, 'vip',
 '{"role_name": "VIP Trial", "duration_days": 7}'::jsonb);
```

### ✏️ Alterar Produtos Existentes

**Alterar nome/preço/descrição:**
```sql
UPDATE products 
SET name = 'Novo Nome', description = 'Nova descrição', price = 79.90
WHERE id = 1;  -- ID do produto
```

**Alterar duração do VIP:**
```sql
UPDATE products 
SET vip_config = '{"role_name": "VIP Gold", "duration_days": 45}'::jsonb
WHERE id = 1;
```

**Transformar em vitalício:**
```sql
UPDATE products 
SET vip_config = '{"role_name": "VIP Eterno", "duration_days": null}'::jsonb
WHERE id = 1;
```

### 🎨 Personalizar Cores das Roles VIP

Edite o arquivo `utils/vip_manager.py` na linha ~15:

```python
self.role_colors = {
    'VIP Bronze': discord.Color.from_rgb(205, 127, 50),     # Bronze
    'VIP Prata': discord.Color.from_rgb(192, 192, 192),     # Prata
    'VIP Ouro': discord.Color.from_rgb(255, 215, 0),        # Ouro
    'VIP Seu Nome': discord.Color.from_rgb(R, G, B),        # Sua cor
}
```

Exemplos de cores:
- Vermelho: `(255, 0, 0)`
- Verde: `(0, 255, 0)`
- Roxo: `(128, 0, 128)`
- Rosa: `(255, 192, 203)`

### 💰 Como os Clientes Compram VIP

```
1. Cliente abre ticket de compra
2. Vê lista de produtos (incluindo todos os VIPs)
3. Escolhe produto VIP desejado
4. Paga via Pix
5. Bot detecta pagamento AUTOMATICAMENTE:
   - Cria role se não existir (com cor personalizada)
   - Adiciona role ao cliente
   - Registra assinatura no banco
   - Envia DM de boas-vindas
6. Sistema gerencia expiração automaticamente
```

### 🔍 Ver Todos os Produtos VIP

```sql
SELECT id, name, price, vip_config->>'role_name' as role, 
       vip_config->>'duration_days' as dias
FROM products WHERE category = 'vip' ORDER BY price ASC;
```

### 🗑️ Remover Produto VIP

```sql
DELETE FROM products WHERE id = 5;
```

---

## 🔮 Roadmap

- [x] Sistema de cupons de desconto ✅
- [x] Sistema VIP com assinaturas ✅
- [ ] Interface web para administração
- [ ] Relatórios de vendas e analytics
- [ ] Integração com outros métodos de pagamento
- [ ] Sistema de avaliações de produtos
- [ ] Notificações push para mobile
- [ ] Sistema de renovação automática VIP

---

**Desenvolvido com ❤️ para a comunidade Discord**
