# Bot de Vendas no Discord com Pagamento via Pix

Este bot de vendas no Discord permite que os usuários escolham produtos, façam pagamentos via Pix e recebam seus produtos automaticamente após confirmação do pagamento. Ele está integrado com o banco de dados **Supabase** e a **PushinPay** para processar pagamentos via Pix.

## 🚀 Funcionalidades

- **Criação de Ticket**: Usuário abre um ticket e o bot cria um canal privado para o atendimento
- **Escolha do Produto**: O bot exibe um modal com produtos disponíveis e o usuário seleciona o produto desejado
- **Geração de Pagamento via Pix**: O bot solicita o e-mail do usuário e gera uma cobrança via Pix com QR Code e código de pagamento
- **Acompanhamento de Pagamento**: O bot monitora o status do pagamento via PushinPay e, após confirmação, entrega o produto automaticamente
- **Entrega do Produto**: O bot realiza a entrega do produto após a confirmação do pagamento, utilizando o banco de dados para registrar transações

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
('Camiseta Estilo 2025', 'Camiseta unissex com estampa futurista, disponível nas cores preta, branca e cinza.', 49.90, 'Roupas'),
('Caneca Personalizada', 'Caneca de cerâmica com design personalizado. Ideal para presentear ou para o seu escritório.', 29.90, 'Acessórios'),
('Fone de Ouvido Bluetooth', 'Fone de ouvido sem fio com cancelamento de ruído. Perfeito para quem busca qualidade de som e conforto.', 199.00, 'Eletrônicos')
ON CONFLICT DO NOTHING;
```

### 3. Convidar Bot para Servidor
1. Acesse: https://discord.com/developers/applications/784058182515425310
2. Vá para "OAuth2" > "URL Generator"
3. Selecione "bot" e "Send Messages"
4. Copie a URL e abra no navegador


## 🎮 Comandos do Bot

- `!start` - Abre um ticket e inicia o processo de compra
- `!products` - Exibe os produtos disponíveis para compra
- `!buy <produto>` - Inicia o processo de pagamento para o produto escolhido
- `!status` - Verifica o status do pagamento e entrega do produto
- `!help` - Exibe a lista de comandos disponíveis

### Comandos Adicionais

- `!list_products` - Lista todos os produtos com detalhes
- `!product_info <nome>` - Informações detalhadas de um produto
- `!search_products <termo>` - Busca produtos por nome ou descrição
- `!payment_history` - Histórico de pagamentos do usuário
- `!payment_details <id>` - Detalhes de uma transação específica
- `!cancel_payment <id>` - Cancela uma transação pendente

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
│   └── payment_utils.py      # Funções para gerar cobrança via Pix
├── config/                   # Arquivos de configuração
│   ├── __init__.py
│   └── config.py            # Configurações do bot
├── data/                     # Armazenamento de dados
│   └── .gitkeep
├── requirements.txt          # Dependências do projeto
├── env.example              # Exemplo de configuração
├── PUSHINPAY_SETUP.md       # Guia de configuração PushinPay
├── CONFIGURACAO_RAPIDA.md   # Guia de configuração rápida
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

O bot vem com 3 produtos de exemplo pré-configurados:

1. **Camiseta Estilo 2025** - R$ 49,90
   - Camiseta unissex com estampa futurista, disponível nas cores preta, branca e cinza

2. **Caneca Personalizada** - R$ 29,90
   - Caneca de cerâmica com design personalizado. Ideal para presentear ou para o seu escritório

3. **Fone de Ouvido Bluetooth** - R$ 199,00
   - Fone de ouvido sem fio com cancelamento de ruído. Perfeito para quem busca qualidade de som e conforto

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
