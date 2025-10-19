# 🛒 Khaos - Bot de Vendas Discord

## 📋 Índice
- [Visão Geral](#-visão-geral)
- [Comandos Principais](#-comandos-principais)
- [Sistema de Tickets](#-sistema-de-tickets)
- [Comandos Admin](#-comandos-admin)
- [Sistema de Pagamento](#-sistema-de-pagamento)
- [Configuração](#-configuração)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

O **Khaos** é um bot de vendas automatizado para Discord que oferece:
- ✅ **Sistema de Tickets** com canais privados
- 💳 **Pagamentos via Pix** com QR Code
- 🤖 **Comandos Slash** modernos (`/`)
- 🎫 **Interface Interativa** com botões e modais
- 🛡️ **Suporte 24/7** automatizado

---

## 📱 Comandos Principais

### `/ajuda`
**Descrição:** Exibe a lista completa de comandos disponíveis  
**Uso:** `/ajuda`  
**Exemplo:** Mostra todos os comandos com descrições e emojis

### `/produtos`
**Descrição:** Lista todos os produtos disponíveis para compra  
**Uso:** `/produtos`  
**Exemplo:** Exibe produtos com preços e descrições

### `/comprar`
**Descrição:** Inicia processo de compra de um produto  
**Uso:** `/comprar <nome_do_produto>`  
**Exemplo:** `/comprar Minecraft Premium`  
**Nota:** ⚠️ Só funciona em canais de ticket

### `/status`
**Descrição:** Verifica o status do seu pagamento  
**Uso:** `/status`  
**Exemplo:** Mostra se o pagamento foi aprovado, pendente ou falhou

---

## 🎫 Sistema de Tickets

### Como Funciona

1. **Admin configura:** Usa `/setup_ticket` em um canal de produtos
2. **Bot envia mensagem:** Com botão "🛒 Criar Ticket de Compra"
3. **Usuário clica:** No botão para abrir modal de seleção
4. **Escolhe produto:** No modal interativo
5. **Canal privado:** É criado automaticamente
6. **Compra:** Usuário usa `/comprar` no canal privado

### Fluxo Completo

```
📢 Canal Público
├── Admin: /setup_ticket
├── Bot: [Mensagem com botão]
└── Usuário: [Clica no botão]

🎫 Modal de Seleção
├── Usuário: [Escolhe produto]
└── Bot: [Cria canal privado]

🔒 Canal Privado
├── Bot: [Mensagem de boas-vindas]
├── Usuário: /comprar
├── Bot: [Gera pagamento Pix]
└── Bot: [Entrega automática]
```

### Vantagens do Sistema

- 🔐 **Privacidade:** Cada compra em canal privado
- 🎯 **Organização:** Produto já selecionado
- 🚀 **Rapidez:** Processo automatizado
- 📊 **Rastreamento:** Fácil acompanhar vendas

---

## 👨‍💼 Comandos Admin

### `/setup_ticket`
**Descrição:** Envia mensagem com botão para criar tickets  
**Uso:** `/setup_ticket`  
**Permissão:** Administrador  
**Exemplo:** Configura sistema de tickets em canal de produtos

### `/close_ticket`
**Descrição:** Fecha um ticket manualmente  
**Uso:** `/close_ticket`  
**Permissão:** Administrador  
**Exemplo:** Fecha ticket após atendimento completo

### Configurações Admin

Para configurar permissões, adicione no `.env`:
```env
ADMIN_ROLE_ID=123456789012345678
TICKET_CATEGORY_ID=123456789012345678
TICKET_LOGS_CHANNEL_ID=123456789012345678
```

---

## 💳 Sistema de Pagamento

### Métodos Suportados
- 🏦 **Pix Instantâneo** (QR Code + Código)
- ⚡ **Confirmação Automática** via webhook
- 🚀 **Entrega Imediata** após pagamento

### Processo de Pagamento

1. **Usuário:** Usa `/comprar` no canal do ticket
2. **Bot:** Gera pagamento via PushinPay
3. **Bot:** Envia QR Code e código Pix
4. **Usuário:** Faz pagamento no app do banco
5. **Sistema:** Detecta pagamento automaticamente
6. **Bot:** Entrega produto instantaneamente

### Status de Pagamento

- 🟡 **Pendente:** Aguardando pagamento
- 🟢 **Aprovado:** Pagamento confirmado
- 🔴 **Falhou:** Pagamento não realizado
- ⏰ **Expirado:** Tempo limite excedido

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` com:

```env
# Discord
DISCORD_TOKEN=seu_token_aqui
DISCORD_APPLICATION_ID=seu_app_id_aqui

# Supabase
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# PushinPay
PUSHINPAY_API_KEY=sua_chave_pushinpay
PUSHINPAY_SANDBOX=true
PUSHINPAY_WEBHOOK_SECRET=seu_webhook_secret

# Webhook
WEBHOOK_BASE_URL=https://seu-dominio.com

# Tickets (Opcional)
TICKET_CATEGORY_ID=id_da_categoria
ADMIN_ROLE_ID=id_do_cargo_admin
TICKET_LOGS_CHANNEL_ID=id_do_canal_de_logs
```

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/Khaos.git
cd Khaos
```

2. **Instale dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure variáveis:**
```bash
cp env.example .env
# Edite o .env com suas credenciais
```

4. **Execute o bot:**
```bash
python bot.py
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### ❌ "Improper token has been passed"
**Solução:** Verifique se o `DISCORD_TOKEN` está correto no `.env`

#### ❌ "SupabaseException: supabase_url is required"
**Solução:** Configure `SUPABASE_URL` e `SUPABASE_KEY` no `.env`

#### ❌ "Shard ID None is requesting privileged intents"
**Solução:** Ative as intents no Discord Developer Portal:
- `SERVER MEMBERS INTENT`
- `MESSAGE CONTENT INTENT`

#### ❌ "Erro ao gerar pagamento"
**Solução:** Verifique se `PUSHINPAY_API_KEY` está configurada

#### ❌ "CommandRegistrationError: The command X is already an existing command"
**Solução:** Reinicie o bot para limpar comandos duplicados

### Logs e Debug

O bot exibe logs detalhados no console:
- ✅ **Conexões:** Database e Discord
- 🔧 **Debug:** Requisições de pagamento
- ❌ **Erros:** Problemas e soluções
- 📊 **Status:** Transações e tickets

### Suporte

Para mais ajuda:
1. Verifique os logs do bot
2. Confirme todas as variáveis de ambiente
3. Teste comandos individualmente
4. Verifique permissões do bot no servidor

---

## 📚 Recursos Adicionais

### Comandos Rápidos
- `!ajuda` - Versão com prefixo (compatibilidade)
- `!produtos` - Lista produtos (compatibilidade)
- `!comprar` - Compra produto (compatibilidade)
- `!status` - Status pagamento (compatibilidade)

### Funcionalidades Avançadas
- 🔄 **Webhooks:** Atualizações automáticas de pagamento
- 📊 **Logs:** Registro de todas as transações
- 🎨 **UI Moderna:** Botões, modais e embeds interativos
- 🔐 **Segurança:** Validação de permissões e dados

### Personalização
- 🎨 **Cores:** Personalize cores dos embeds
- 📝 **Mensagens:** Customize textos do bot
- 🏷️ **Categorias:** Organize tickets por categoria
- 📋 **Logs:** Configure canal de logs personalizado

---

**Desenvolvido com ❤️ para automatizar vendas no Discord**
