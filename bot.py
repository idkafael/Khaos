import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
import json

# Importações dos módulos
from commands.product_commands import ProductCommands
from commands.payment_commands import PaymentCommands
from models.product_model import ProductModel
from models.transaction_model import TransactionModel
from utils.payment_utils import PaymentUtils
from config.config import Config

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Inicializar modelos
product_model = ProductModel()
transaction_model = TransactionModel()
payment_utils = PaymentUtils()

# Dicionário para armazenar tickets ativos
active_tickets = {}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    print(f'ID: {bot.user.id}')
    print(f'Guilds: {len(bot.guilds)}')
    
    # Inicializar banco de dados
    await product_model.initialize()
    await transaction_model.initialize()
    
    # Carregar produtos de exemplo se não existirem
    await load_sample_products()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argumento obrigatório ausente: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argumento inválido fornecido.")
    else:
        print(f"Erro não tratado: {error}")
        await ctx.send("❌ Ocorreu um erro inesperado. Tente novamente.")

async def load_sample_products():
    """Carrega produtos de exemplo no banco de dados"""
    products = await product_model.get_all_products()
    if not products:
        sample_products = [
            {
                "name": "Camiseta Estilo 2025",
                "description": "Camiseta unissex com estampa futurista, disponível nas cores preta, branca e cinza.",
                "price": 49.90,
                "category": "Roupas"
            },
            {
                "name": "Caneca Personalizada",
                "description": "Caneca de cerâmica com design personalizado. Ideal para presentear ou para o seu escritório.",
                "price": 29.90,
                "category": "Acessórios"
            },
            {
                "name": "Fone de Ouvido Bluetooth",
                "description": "Fone de ouvido sem fio com cancelamento de ruído. Perfeito para quem busca qualidade de som e conforto.",
                "price": 199.00,
                "category": "Eletrônicos"
            }
        ]
        
        for product in sample_products:
            await product_model.create_product(product)

@bot.command(name='start')
async def start_ticket(ctx):
    """Inicia um ticket de compra"""
    user_id = ctx.author.id
    guild = ctx.guild
    
    # Verificar se já existe um ticket ativo para o usuário
    if user_id in active_tickets:
        await ctx.send("❌ Você já possui um ticket ativo! Use `!status` para verificar o progresso.")
        return
    
    # Criar canal privado para o ticket
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    try:
        ticket_channel = await guild.create_text_channel(
            f'ticket-{ctx.author.name}',
            overwrites=overwrites,
            category=None
        )
        
        # Armazenar informações do ticket
        active_tickets[user_id] = {
            'channel_id': ticket_channel.id,
            'user_id': user_id,
            'status': 'active',
            'created_at': datetime.now()
        }
        
        # Enviar mensagem de boas-vindas
        embed = discord.Embed(
            title="🛒 Ticket de Compra Criado!",
            description=f"Olá {ctx.author.mention}! Bem-vindo ao nosso sistema de vendas.",
            color=0x00ff00
        )
        embed.add_field(
            name="📋 Próximos Passos",
            value="1. Use `!products` para ver os produtos disponíveis\n2. Use `!buy <produto>` para comprar um produto\n3. Use `!status` para verificar o progresso",
            inline=False
        )
        embed.set_footer(text="Digite !help para ver todos os comandos disponíveis")
        
        await ticket_channel.send(embed=embed)
        await ctx.send(f"✅ Ticket criado com sucesso! Acesse {ticket_channel.mention}")
        
    except Exception as e:
        print(f"Erro ao criar ticket: {e}")
        await ctx.send("❌ Erro ao criar ticket. Tente novamente.")

@bot.command(name='products')
async def show_products(ctx):
    """Exibe os produtos disponíveis"""
    try:
        products = await product_model.get_all_products()
        
        if not products:
            await ctx.send("❌ Nenhum produto disponível no momento.")
            return
        
        embed = discord.Embed(
            title="🛍️ Produtos Disponíveis",
            description="Escolha um produto para comprar:",
            color=0x0099ff
        )
        
        for product in products:
            embed.add_field(
                name=f"🛒 {product['name']}",
                value=f"**Preço:** R$ {product['price']:.2f}\n**Descrição:** {product['description']}",
                inline=False
            )
        
        embed.set_footer(text="Use !buy <nome_do_produto> para comprar")
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        await ctx.send("❌ Erro ao carregar produtos. Tente novamente.")

@bot.command(name='buy')
async def buy_product(ctx, *, product_name):
    """Inicia o processo de compra de um produto"""
    try:
        # Buscar produto no banco de dados
        product = await product_model.get_product_by_name(product_name)
        
        if not product:
            await ctx.send("❌ Produto não encontrado. Use `!products` para ver os produtos disponíveis.")
            return
        
        # Verificar se o usuário tem um ticket ativo
        user_id = ctx.author.id
        if user_id not in active_tickets:
            await ctx.send("❌ Você precisa criar um ticket primeiro! Use `!start` para começar.")
            return
        
        # Criar transação
        transaction = await transaction_model.create_transaction(
            user_id=user_id,
            product_id=product['id'],
            amount=product['price'],
            status='pending'
        )
        
        # Gerar pagamento via Pix diretamente
        payment_data = await payment_utils.create_pix_payment(
            amount=product['price'],
            description=f"Compra: {product['name']}",
            customer_email=f"{ctx.author.name}@discord.com",  # Email padrão baseado no nome
            customer_name=ctx.author.name
        )
        
        if payment_data:
            # Atualizar transação com payment_id
            await transaction_model.update_transaction(transaction['id'], {
                'payment_id': payment_data['id'],
                'pix_code': payment_data['pix_code'],
                'qr_code': payment_data['qr_code'],
                'email': f"{ctx.author.name}@discord.com"
            })
            
            # Exibir informações de pagamento
            embed = discord.Embed(
                title="💳 Pagamento via Pix",
                description=f"**Produto:** {product['name']}\n**Valor:** R$ {product['price']:.2f}",
                color=0x00ff00
            )
            embed.add_field(
                name="📱 Código Pix",
                value=f"```{payment_data['pix_code']}```",
                inline=False
            )
            embed.add_field(
                name="⏰ Tempo para pagamento",
                value="10 minutos",
                inline=True
            )
            embed.set_footer(text="Escaneie o QR Code ou copie o código Pix")
            
            await ctx.send(embed=embed)
            
            # Enviar QR Code como imagem se disponível
            if payment_data.get('qr_code_base64'):
                # Usar QR Code base64 da PushinPay
                qr_image = payment_utils.get_qr_code_image_from_base64(payment_data['qr_code_base64'])
                if qr_image:
                    await ctx.send(file=discord.File(qr_image, filename='qrcode.png'))
            elif payment_data.get('qr_code_image'):
                # Fallback para QR Code gerado localmente
                await ctx.send(file=discord.File(payment_data['qr_code_image']))
            
            # Atualizar status do ticket
            active_tickets[user_id]['transaction_id'] = transaction['id']
            active_tickets[user_id]['product'] = product
            active_tickets[user_id]['status'] = 'waiting_payment'
            
            # Iniciar monitoramento do pagamento
            asyncio.create_task(monitor_payment(transaction['id'], user_id))
            
        else:
            await ctx.send("❌ Erro ao gerar pagamento. Tente novamente.")
        
    except Exception as e:
        print(f"Erro ao iniciar compra: {e}")
        await ctx.send("❌ Erro ao iniciar processo de compra. Tente novamente.")

@bot.command(name='status')
async def check_status(ctx):
    """Verifica o status do pagamento e entrega"""
    user_id = ctx.author.id
    
    if user_id not in active_tickets:
        await ctx.send("❌ Você não possui um ticket ativo. Use `!start` para começar.")
        return
    
    ticket = active_tickets[user_id]
    
    if 'transaction_id' not in ticket:
        await ctx.send("✅ Ticket ativo, mas nenhuma compra iniciada. Use `!buy <produto>` para comprar.")
        return
    
    try:
        # Buscar transação no banco de dados
        transaction = await transaction_model.get_transaction(ticket['transaction_id'])
        
        if not transaction:
            await ctx.send("❌ Transação não encontrada.")
            return
        
        embed = discord.Embed(
            title="📊 Status da Compra",
            color=0x0099ff
        )
        
        embed.add_field(
            name="🛒 Produto",
            value=ticket['product']['name'],
            inline=True
        )
        embed.add_field(
            name="💰 Valor",
            value=f"R$ {transaction['amount']:.2f}",
            inline=True
        )
        embed.add_field(
            name="📈 Status",
            value=transaction['status'].upper(),
            inline=True
        )
        
        if transaction['status'] == 'approved':
            embed.add_field(
                name="✅ Entrega",
                value="Produto entregue com sucesso!",
                inline=False
            )
        elif transaction['status'] == 'pending':
            embed.add_field(
                name="⏳ Aguardando",
                value="Aguardando confirmação do pagamento...",
                inline=False
            )
        elif transaction['status'] == 'failed':
            embed.add_field(
                name="❌ Falha",
                value="Pagamento não foi confirmado.",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        await ctx.send("❌ Erro ao verificar status. Tente novamente.")

@bot.event
async def on_message(message):
    """Processa mensagens normalmente"""
    if message.author.bot:
        return
    
    # Processar comandos normalmente
    await bot.process_commands(message)

async def monitor_payment(transaction_id, user_id):
    """Monitora o status do pagamento"""
    try:
        # Aguardar um pouco antes de começar a verificar
        await asyncio.sleep(30)
        
        max_attempts = 20  # Verificar por 10 minutos (30s * 20)
        attempts = 0
        
        while attempts < max_attempts:
            # Verificar status do pagamento
            payment_status = await payment_utils.check_payment_status(transaction_id)
            
            if payment_status == 'approved':
                # Atualizar transação como aprovada
                await transaction_model.update_transaction(transaction_id, {'status': 'approved'})
                
                # Enviar confirmação
                if user_id in active_tickets:
                    channel_id = active_tickets[user_id]['channel_id']
                    channel = bot.get_channel(channel_id)
                    
                    if channel:
                        embed = discord.Embed(
                            title="✅ Pagamento Aprovado!",
                            description="Seu pagamento foi confirmado com sucesso!",
                            color=0x00ff00
                        )
                        embed.add_field(
                            name="🎉 Produto Entregue",
                            value="Seu produto foi entregue digitalmente. Obrigado pela compra!",
                            inline=False
                        )
                        embed.set_footer(text="Use !status para verificar o histórico")
                        
                        await channel.send(embed=embed)
                        
                        # Limpar ticket ativo
                        del active_tickets[user_id]
                
                break
            elif payment_status == 'failed':
                # Atualizar transação como falhada
                await transaction_model.update_transaction(transaction_id, {'status': 'failed'})
                
                # Enviar notificação de falha
                if user_id in active_tickets:
                    channel_id = active_tickets[user_id]['channel_id']
                    channel = bot.get_channel(channel_id)
                    
                    if channel:
                        await channel.send("❌ Pagamento não foi confirmado. Tente novamente com `!buy <produto>`")
                        
                        # Limpar ticket ativo
                        del active_tickets[user_id]
                
                break
            
            # Aguardar antes da próxima verificação
            await asyncio.sleep(30)
            attempts += 1
        
        # Se excedeu o tempo limite
        if attempts >= max_attempts:
            if user_id in active_tickets:
                channel_id = active_tickets[user_id]['channel_id']
                channel = bot.get_channel(channel_id)
                
                if channel:
                    await channel.send("⏰ Tempo limite para pagamento expirado. Use `!buy <produto>` para tentar novamente.")
                    
                    # Limpar ticket ativo
                    del active_tickets[user_id]
                    
    except Exception as e:
        print(f"Erro ao monitorar pagamento: {e}")

@bot.command(name='ajuda')
async def help_command(ctx):
    """Exibe a lista de comandos disponíveis"""
    embed = discord.Embed(
        title="🤖 Comandos do Bot de Vendas",
        description="Lista de comandos disponíveis:",
        color=0x0099ff
    )
    
    commands_list = [
        ("!start", "Cria um ticket e inicia o processo de compra"),
        ("!products", "Exibe os produtos disponíveis para compra"),
        ("!buy <produto>", "Inicia o processo de pagamento para o produto escolhido"),
        ("!status", "Verifica o status do pagamento e entrega do produto"),
        ("!help", "Exibe esta lista de comandos")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Para mais informações, consulte a documentação do projeto")
    await ctx.send(embed=embed)

# Executar o bot
if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")
