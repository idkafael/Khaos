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
from utils.ticket_views import TicketView, TicketChannelView
from utils.ticket_manager import TicketManager
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
ticket_manager = TicketManager()

# Dicionário para armazenar tickets ativos
active_tickets = {}

# Função auxiliar para responder comandos
async def respond_command(ctx, message, embed=None, ephemeral=False):
    """Responde comandos tanto slash quanto prefixo"""
    if ctx.interaction:
        if embed:
            await ctx.respond(embed=embed, ephemeral=ephemeral)
        else:
            await ctx.respond(message, ephemeral=ephemeral)
    else:
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(message)

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
    
    # Adicionar view persistente para tickets
    bot.add_view(TicketView())
    bot.add_view(TicketChannelView())
    
    print("✅ Bot inicializado com sistema de tickets!")

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

# ==================== SLASH COMMANDS ====================

@bot.hybrid_command(name="setup_ticket", description="[ADMIN] Enviar mensagem para criar tickets")
@commands.has_permissions(administrator=True)
async def setup_ticket_command(ctx):
    """Comando admin para enviar mensagem com botão de criar ticket"""
    try:
        success = await ticket_manager.send_ticket_embed(ctx.channel)
        if success:
            if ctx.interaction:
                await ctx.respond("✅ Mensagem de ticket enviada com sucesso!", ephemeral=True)
            else:
                await ctx.send("✅ Mensagem de ticket enviada com sucesso!")
        else:
            if ctx.interaction:
                await ctx.respond("❌ Erro ao enviar mensagem de ticket.", ephemeral=True)
            else:
                await ctx.send("❌ Erro ao enviar mensagem de ticket.")
    except Exception as e:
        print(f"Erro no comando setup_ticket: {e}")
        if ctx.interaction:
            await ctx.respond("❌ Erro ao configurar sistema de tickets.", ephemeral=True)
        else:
            await ctx.send("❌ Erro ao configurar sistema de tickets.")

@bot.hybrid_command(name="ajuda", description="Exibe a lista de comandos disponíveis")
async def help_command(ctx):
    """Exibe a lista de comandos disponíveis"""
    embed = discord.Embed(
        title="🛒 Comandos de Khaos",
        description="Sistema completo de vendas com tickets e pagamentos via Pix",
        color=0xe91e63
    )
    
    embed.add_field(
        name="» Sistema de Tickets",
        value="Clique no botão 'Criar Ticket de Compra' para começar\nEscolha seu produto no modal interativo\nAcesse seu canal privado para continuar",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos Principais",
        value="`/ajuda` :: 🤖 Lista de comandos\n`/produtos` :: 🛍️ Ver produtos disponíveis\n`/comprar` :: 💳 Comprar produto (no canal do ticket)\n`/status` :: 📊 Status do pagamento",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos Admin",
        value="`/setup_ticket` :: ⚙️ Enviar mensagem de tickets\n`/close_ticket` :: 🔒 Fechar ticket manualmente",
        inline=False
    )
    
    embed.add_field(
        name="» Sistema de Pagamento",
        value="💎 **Pix Instantâneo** - QR Code + Código\n🚀 **Entrega Automática** - Após confirmação\n🛡️ **Suporte 24/7** - Atendimento completo",
        inline=False
    )
    
    embed.set_footer(text="Sistema de vendas automatizado • Powered by Khaos")
    if ctx.interaction:
        await ctx.respond(embed=embed)
    else:
        await ctx.send(embed=embed)

@bot.hybrid_command(name="produtos", description="Ver produtos disponíveis")
async def show_products_slash(ctx):
    """Exibe os produtos disponíveis via slash command"""
    try:
        products = await product_model.get_all_products()
        
        if not products:
            if ctx.interaction:
                await ctx.respond("❌ Nenhum produto disponível no momento.")
            else:
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
        
        embed.set_footer(text="Crie um ticket para comprar um produto")
        if ctx.interaction:
            await ctx.respond(embed=embed)
        else:
            await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        if ctx.interaction:
            await ctx.respond("❌ Erro ao carregar produtos. Tente novamente.")
        else:
            await ctx.send("❌ Erro ao carregar produtos. Tente novamente.")

@bot.hybrid_command(name="comprar", description="Comprar produto (use no canal do ticket)")
async def buy_product_slash(ctx, produto: str = None):
    """Inicia o processo de compra de um produto via slash command"""
    try:
        # Verificar se está em canal de ticket
        if not ctx.channel.name.startswith('ticket-'):
            if ctx.interaction:
                await ctx.respond("❌ Este comando só pode ser usado em canais de ticket.", ephemeral=True)
            else:
                await ctx.send("❌ Este comando só pode ser usado em canais de ticket.")
            return
        
        # Verificar se o usuário tem um ticket ativo
        user_id = ctx.author.id
        if user_id not in active_tickets:
            if ctx.interaction:
                await ctx.respond("❌ Você não possui um ticket ativo.", ephemeral=True)
            else:
                await ctx.send("❌ Você não possui um ticket ativo.")
            return
        
        # Usar produto do ticket se não especificado
        if not produto:
            ticket_data = active_tickets[user_id]
            if 'product_name' in ticket_data:
                produto = ticket_data['product_name']
            else:
                await ctx.respond("❌ Nenhum produto especificado. Use: `/comprar produto: Nome do Produto`", ephemeral=True)
                return
        
        # Buscar produto no banco de dados
        product = await product_model.get_product_by_name(produto)
        
        if not product:
            await ctx.respond("❌ Produto não encontrado. Use `/produtos` para ver os produtos disponíveis.", ephemeral=True)
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
            customer_email=f"{ctx.author.name}@discord.com",
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
            
            await ctx.respond(embed=embed)
            
            # Enviar QR Code como imagem se disponível
            if payment_data.get('qr_code_base64'):
                # Usar QR Code base64 da PushinPay
                qr_image = payment_utils.get_qr_code_image_from_base64(payment_data['qr_code_base64'])
                if qr_image:
                    await ctx.followup.send(file=discord.File(qr_image, filename='qrcode.png'))
            elif payment_data.get('qr_code_image'):
                # Fallback para QR Code gerado localmente
                await ctx.followup.send(file=discord.File(payment_data['qr_code_image']))
            
            # Atualizar status do ticket
            active_tickets[user_id]['status'] = 'waiting_payment'
            
            # Iniciar monitoramento do pagamento
            asyncio.create_task(monitor_payment(transaction['id'], user_id))
            
        else:
            await ctx.respond("❌ Erro ao gerar pagamento. Tente novamente.", ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao iniciar compra: {e}")
        await ctx.respond("❌ Erro ao iniciar processo de compra. Tente novamente.", ephemeral=True)

@bot.hybrid_command(name="status", description="Verificar status do pagamento")
async def check_status_slash(ctx):
    """Verifica o status do pagamento via slash command"""
    user_id = ctx.author.id
    
    if user_id not in active_tickets:
        await ctx.respond("❌ Você não possui um ticket ativo.", ephemeral=True)
        return
    
    ticket = active_tickets[user_id]
    
    if 'transaction_id' not in ticket:
        await ctx.respond("✅ Ticket ativo, mas nenhuma compra iniciada. Use `/comprar` para comprar.", ephemeral=True)
        return
    
    try:
        # Buscar transação no banco de dados
        transaction = await transaction_model.get_transaction(ticket['transaction_id'])
        
        if not transaction:
            await ctx.respond("❌ Transação não encontrada.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Status da Compra",
            color=0x0099ff
        )
        
        embed.add_field(
            name="🛒 Produto",
            value=ticket['product_name'],
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
        
        await ctx.respond(embed=embed)
        
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        await ctx.respond("❌ Erro ao verificar status. Tente novamente.", ephemeral=True)

@bot.hybrid_command(name="close_ticket", description="[ADMIN] Fechar ticket manualmente")
@commands.has_permissions(administrator=True)
async def close_ticket_slash(ctx):
    """Fecha um ticket manualmente via slash command"""
    try:
        # Verificar se é canal de ticket
        if not ctx.channel.name.startswith('ticket-'):
            await ctx.respond("❌ Este comando só pode ser usado em canais de ticket.", ephemeral=True)
            return
        
        # Fechar ticket
        success, message = await ticket_manager.close_ticket(ctx.channel, ctx.author)
        
        if success:
            await ctx.respond(f"✅ {message}")
            # Deletar canal após 5 segundos
            await asyncio.sleep(5)
            await ctx.channel.delete()
        else:
            await ctx.respond(f"❌ {message}")
            
    except Exception as e:
        print(f"Erro ao fechar ticket: {e}")
        await ctx.respond("❌ Erro ao fechar ticket. Tente novamente.", ephemeral=True)

# ==================== COMANDOS DE PREFIXO (COMPATIBILIDADE) ====================

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
            await ctx.send("❌ Você precisa criar um ticket primeiro! Use o botão 'Criar Ticket de Compra' para começar.")
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


# Executar o bot
if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")
