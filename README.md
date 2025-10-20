# Bot de Vendas no Discord com Sistema de Tickets e Pagamento via Pix

Bot moderno de vendas no Discord com sistema de tickets automatizado, interface com botões e modals, comandos slash, e integração completa com **Supabase** e **PushinPay** para processamento de pagamentos via Pix.

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
```

### 2. Configurar Supabase
1. Acesse: https://supabase.com/dashboard
2. Vá para "SQL Editor"
3. Execute este SQL:

```sql
-- Tabela de produtos
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de transações
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id INTEGER REFERENCES products(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    email VARCHAR(255),
    payment_id VARCHAR(255),
    pix_code TEXT,
    qr_code TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

-- Produtos de exemplo
INSERT INTO products (name, description, price, category) VALUES
('Minecraft Premium', 'Conta Minecraft Premium original com acesso completo ao jogo. Inclui skin personalizada e histórico limpo.', 45.00, 'Jogos Digitais'),
('Spotify Premium', 'Conta Spotify Premium válida por 3 meses. Música sem anúncios, download offline e qualidade máxima.', 25.00, 'Streaming'),
('Netflix Premium', 'Conta Netflix Premium compartilhada por 1 mês. Acesso completo a todos os conteúdos em 4K.', 35.00, 'Streaming'),
('Discord Nitro', 'Discord Nitro válido por 1 mês. Uploads maiores, emojis personalizados e boost de servidor.', 20.00, 'Gaming'),
('Adobe Creative Cloud', 'Acesso completo ao Adobe Creative Cloud por 1 mês. Photoshop, Illustrator, Premiere Pro e mais.', 80.00, 'Software'),
('Office 365', 'Microsoft Office 365 válido por 1 ano. Word, Excel, PowerPoint e OneDrive com 1TB.', 60.00, 'Software'),
('Steam Wallet', 'Saldo Steam Wallet de R$ 50,00. Use para comprar jogos, DLCs e itens na Steam.', 50.00, 'Gaming'),
('YouTube Premium', 'YouTube Premium por 3 meses. Sem anúncios, downloads offline e YouTube Music incluído.', 30.00, 'Streaming')
ON CONFLICT DO NOTHING;
```

### 3. Configurar Sistema de Tickets (Opcional)
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

### 4. Convidar Bot para Servidor
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
- `/comprar` - Comprar produto (no canal do ticket)
- `/status` - Verificar status do pagamento
- `/setup_ticket` - [ADMIN] Enviar mensagem de tickets
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
4. **Comprar**: Use `/comprar` no canal do ticket para gerar pagamento
5. **Acompanhar**: Use `/status` para verificar o progresso do pagamento

### Fluxo Completo:
```
Admin → /setup_ticket → Botão aparece
Usuário → Clica botão → Modal com produtos
Usuário → Escolhe produto → Canal privado criado
Usuário → /comprar → Pagamento Pix gerado
Usuário → Paga → Bot detecta → Entrega automática
```

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

### Erro de Conexão com Supabase
- Verifique se as credenciais estão corretas
- Confirme se as tabelas foram criadas
- Verifique se o projeto está ativo

### Erro de Pagamento OpenPix
- Verifique se a API Key está correta
- Confirme se a conta está ativa
- Verifique os logs para mais detalhes

### Bot não responde
- Verifique se o token do Discord está correto
- Confirme se as intents estão habilitadas
- Verifique se o bot tem permissões no servidor

## 📝 Logs

O bot gera logs detalhados em:
- Console (desenvolvimento)
- Arquivo `bot.log` (produção)

Níveis de log configuráveis via variável `LOG_LEVEL`.

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

## 🔮 Roadmap

- [ ] Interface web para administração
- [ ] Sistema de cupons de desconto
- [ ] Relatórios de vendas
- [ ] Integração com outros métodos de pagamento
- [ ] Sistema de avaliações de produtos
- [ ] Notificações push para mobile

---

**Desenvolvido com ❤️ para a comunidade Discord**
