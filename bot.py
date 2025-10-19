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

# Adicionar comandos slash manualmente
@bot.tree.command(name="teste", description="Comando de teste")
async def teste_slash(interaction: discord.Interaction):
    """Comando de teste simples"""
    print(f"Comando /teste executado por {interaction.user.name} em {interaction.guild.name}")
    embed = discord.Embed(
        description="✅ Comando de teste funcionando!",
        color=0x8B5CF6
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setup_ticket", description="[ADMIN] Configurar sistema de tickets")
@discord.app_commands.default_permissions(administrator=True)
async def setup_ticket_slash(interaction: discord.Interaction):
    """Comando admin para configurar sistema de tickets via modal"""
    try:
        print(f"Comando setup_ticket executado por {interaction.user.name}")
        print("Tentando importar SetupTicketModal...")
        
        from utils.ticket_views import SetupTicketModal
        print("SetupTicketModal importado com sucesso!")
        
        print("Criando instância do modal...")
        modal = SetupTicketModal()
        print("Modal criado com sucesso!")
        
        print("Enviando modal...")
        await interaction.response.send_modal(modal)
        print("Modal enviado com sucesso!")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            description="❌ Erro de importação no sistema de tickets.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Erro no comando setup_ticket: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            description="❌ Erro ao configurar sistema de tickets.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ajuda", description="Exibe a lista de comandos disponíveis")
async def ajuda_slash(interaction: discord.Interaction):
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
    
    side_embed = discord.Embed(
        description="📋 Lista de comandos disponíveis:",
        color=0x8B5CF6
    )
    
    await interaction.response.send_message(embeds=[embed, side_embed])

@bot.tree.command(name="produtos", description="Ver produtos disponíveis")
async def produtos_slash(interaction: discord.Interaction):
    """Exibe os produtos disponíveis via slash command"""
    try:
        products = await product_model.get_all_products()
        
        if not products:
            embed = discord.Embed(
                description="❌ Nenhum produto disponível no momento.",
                color=0x8B5CF6
            )
            await interaction.response.send_message(embed=embed)
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
        
        side_embed = discord.Embed(
            description="🛍️ Produtos disponíveis:",
            color=0x8B5CF6
        )
        
        await interaction.response.send_message(embeds=[embed, side_embed])
        
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        embed = discord.Embed(
            description="❌ Erro ao carregar produtos. Tente novamente.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed)

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

async def respond_with_side_embed(ctx, message, embed=None, ephemeral=False):
    """Responde apenas com embed lateral roxo"""
    # Criar embed lateral roxo simples apenas com a mensagem
    side_embed = discord.Embed(
        description=message,
        color=0x8B5CF6  # Roxo
    )
    
    # Se já tem um embed principal, enviar apenas ambos embeds
    if embed:
        if ctx.interaction:
            await ctx.respond(embeds=[embed, side_embed], ephemeral=ephemeral)
        else:
            await ctx.send(embeds=[embed, side_embed])
    else:
        # Se não tem embed principal, enviar apenas embed lateral
        if ctx.interaction:
            await ctx.respond(embed=side_embed, ephemeral=ephemeral)
        else:
            await ctx.send(embed=side_embed)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    print(f'ID: {bot.user.id}')
    print(f'Guilds: {len(bot.guilds)}')
    
    # Listar guilds conectadas
    for guild in bot.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")
    
    # Sincronizar comandos slash
    try:
        print("🔄 Sincronizando comandos slash...")
        
        # Aguardar um pouco para garantir que o bot está totalmente conectado
        await asyncio.sleep(2)
        
        # Listar comandos registrados antes da sincronização
        commands = bot.tree.get_commands()
        print(f"📋 Comandos registrados no bot: {len(commands)}")
        for cmd in commands:
            print(f"  - /{cmd.name}: {cmd.description}")
        
        # Tentar sincronizar globalmente
        try:
            print("🌍 Tentando sincronização global...")
            synced = await bot.tree.sync()
            print(f"✅ {len(synced)} comandos sincronizados globalmente!")
            
            # Aguardar um pouco para a sincronização se propagar
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"❌ Erro na sincronização global: {e}")
            print("🏠 Tentando sincronização por guild...")
            
            # Tentar sincronizar por guild
            for guild in bot.guilds:
                try:
                    print(f"🔄 Sincronizando na guild: {guild.name} (ID: {guild.id})")
                    synced = await bot.tree.sync(guild=guild)
                    print(f"✅ {len(synced)} comandos sincronizados na guild {guild.name}!")
                    
                    # Aguardar um pouco entre sincronizações
                    await asyncio.sleep(1)
                    
                except Exception as guild_error:
                    print(f"❌ Erro na guild {guild.name}: {guild_error}")
                    import traceback
                    traceback.print_exc()
        
        # Verificar se os comandos estão disponíveis
        print("🔍 Verificando comandos disponíveis...")
        try:
            # Tentar acessar os comandos do bot
            app_commands = bot.tree.get_commands()
            print(f"📊 Total de comandos app_commands: {len(app_commands)}")
            
            # Verificar se o bot tem as permissões necessárias
            print(f"🔑 Bot ID: {bot.user.id}")
            print(f"🔑 Application ID: {Config.DISCORD_APPLICATION_ID}")
            
        except Exception as e:
            print(f"❌ Erro ao verificar comandos: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Erro geral na sincronização: {e}")
        import traceback
        traceback.print_exc()
    
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


# Comando de teste via prefixo
@bot.command(name='teste')
async def teste_prefix(ctx):
    """Comando de teste via prefixo"""
    print(f"Comando !teste executado por {ctx.author.name} em {ctx.guild.name}")
    await respond_with_side_embed(ctx, "✅ Comando de teste funcionando via prefixo!")

# Comando para forçar sincronização de slash commands
@bot.command(name='sync')
@commands.has_permissions(administrator=True)
async def sync_commands(ctx):
    """Força a sincronização dos comandos slash"""
    try:
        print(f"🔄 Comando de sincronização executado por {ctx.author.name}")
        
        # Listar comandos registrados
        commands = bot.tree.get_commands()
        await ctx.send(f"📋 Comandos registrados: {len(commands)}")
        for cmd in commands:
            await ctx.send(f"  - /{cmd.name}: {cmd.description}")
        
        # Tentar sincronizar globalmente
        try:
            synced = await bot.tree.sync()
            await ctx.send(f"✅ {len(synced)} comandos sincronizados globalmente!")
        except Exception as e:
            await ctx.send(f"❌ Erro na sincronização global: {e}")
            
            # Tentar sincronizar por guild
            synced = await bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ {len(synced)} comandos sincronizados na guild!")
            
    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

# Comando para configurar ticket com imagem
@bot.command(name='setup_ticket_img')
@commands.has_permissions(administrator=True)
async def setup_ticket_with_image(ctx):
    """Configura sistema de tickets - envie uma imagem junto com o comando"""
    try:
        # Verificar se há anexos
        if not ctx.message.attachments:
            await ctx.send("❌ Envie uma imagem junto com o comando! Ex: `!setup_ticket_img` + imagem")
            return
        
        # Pegar a primeira imagem
        attachment = ctx.message.attachments[0]
        
        # Verificar se é uma imagem
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            await ctx.send("❌ O arquivo deve ser uma imagem!")
            return
        
        # Criar embed com a imagem
        embed = discord.Embed(
            title="🛒 Sistema de Vendas Automatizado",
            description="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            color=0x0099ff
        )
        embed.set_image(url=attachment.url)
        embed.add_field(
            name="🚀 Como Funciona?",
            value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
            inline=False
        )
        embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")
        
        # Criar view com botão
        from utils.ticket_views import TicketView
        view = TicketView("Criar Ticket de Compra")
        
        await ctx.send(embed=embed, view=view)
        await ctx.send("✅ Sistema de tickets configurado com imagem!")
        
    except Exception as e:
        print(f"Erro no setup_ticket_img: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send("❌ Erro ao configurar sistema de tickets.")

# Executar o bot
if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")
