import disnake
from disnake.ext import commands
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
from utils.log_system import LogSystem
from config.config import Config

# Configuração do bot
intents = disnake.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix='?',
    intents=intents,
    help_command=None  # Desabilitar help padrão
)
# Deploy: 24/10/2025 15:35 - Fix InputText

# Adicionar comandos slash manualmente
@bot.slash_command(name="teste", description="Comando de teste")
async def teste_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando de teste simples"""
    print(f"Comando /teste executado por {inter.user.name} em {inter.guild.name}")
    embed = disnake.Embed(
        description="✅ Comando de teste funcionando!",
        color=0x8B5CF6
    )
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="teste_modal", description="[ADMIN] Testar funcionamento dos modais")
@commands.has_permissions(administrator=True)
async def teste_modal_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando admin para testar se os modais estão funcionando"""
    try:
        print(f"🔧 Comando teste_modal executado por {inter.user.name}")
        
        from utils.ticket_views import SetupMessageModal
        print("✅ SetupMessageModal importado com sucesso!")
        
        modal = SetupMessageModal()
        print("✅ Modal de teste criado com sucesso!")
        
        await inter.response.send_modal(modal)
        print("✅ Modal de teste enviado com sucesso!")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro de importação no sistema de modais.",
            color=0xff0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"❌ Erro no comando teste_modal: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao testar modais.",
            color=0xff0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="get_emotes")
async def get_emotes(ctx):
    """Comando para listar todos os emojis do servidor com IDs e nomes"""
    try:
        guild = ctx.guild
        
        # Buscar todos os emojis do servidor
        emojis = [emoji for emoji in guild.emojis if emoji.available]
        
        if not emojis:
            await ctx.send("❌ Este servidor não possui emojis customizados.")
            return

        # Ordenar por nome
        emojis_sorted = sorted(emojis, key=lambda e: e.name.lower())
        
        # Criar embed
        embed = disnake.Embed(
            title=f"📋 Emojis do Servidor: {guild.name}",
            description=f"Total de emojis: **{len(emojis)}**",
            color=0x8B5CF6
        )
        
        # Dividir em chunks de 10 para evitar limite do Discord
        chunk_size = 10
        for i in range(0, len(emojis_sorted), chunk_size):
            chunk = emojis_sorted[i:i + chunk_size]
            
            field_value = ""
            for emoji in chunk:
                emoji_str = f"{emoji} `:{emoji.name}:`"
                emoji_id = f"ID: `{emoji.id}`"
                field_value += f"{emoji_str} - {emoji_id}\n"
            
            field_name = f"Emojis {i+1}-{min(i+chunk_size, len(emojis_sorted))}"
            embed.add_field(name=field_name, value=field_value, inline=False)
        
        # Adicionar footer com instruções
        embed.set_footer(text="💡 Copie o formato <:nome:ID> para usar em qualquer servidor")
        
        # Criar mensagem de texto para fácil cópia
        text_content = "```python\n# IDs dos Emojis para usar no código:\n"
        text_content += "EMOJI_IDS = {\n"
        for emoji in emojis_sorted:
            text_content += f'    "{emoji.name}": {emoji.id},\n'
        text_content += "}\n```"
        
        # Enviar embed
        await ctx.send(embed=embed)
        
        # Enviar código formatado
        if len(text_content) <= 2000:
            await ctx.send(text_content)
        
    except Exception as e:
        print(f"❌ Erro ao buscar emojis: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Erro ao buscar emojis: {str(e)[:200]}")

@bot.slash_command(name="setup_ticket", description="[ADMIN] Configurar sistema de tickets")
@commands.has_permissions(administrator=True)
async def setup_ticket_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando admin para configurar sistema de tickets via interface interativa"""
    try:
        print(f"🔧 Comando setup_ticket executado por {inter.user.name}")
        
        from utils.ticket_views import ObjectiveSelectionView
        print("✅ ObjectiveSelectionView importado com sucesso!")
        
        # Criar view de seleção de objetivo
        view = ObjectiveSelectionView(inter.guild_id)
        print("✅ View de seleção criada com sucesso!")
        
        # Criar embed inicial
        embed = disnake.Embed(
            title="⚙️ Configuração de Sistema de Tickets",
            description="**Selecione o objetivo do ticket:**\n\nEscolha uma das opções abaixo para configurar o tipo de ticket desejado.",
            color=0x8B5CF6
        )
        embed.add_field(
            name="💡 Dica",
            value="Você poderá configurar todos os detalhes após selecionar o objetivo.",
            inline=False
        )
        
        # Enviar view inicial
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
        print("✅ View inicial enviada com sucesso!")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro de importação no sistema de tickets.",
            color=0xff0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"❌ Erro no comando setup_ticket: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao configurar sistema de tickets.",
            color=0xff0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="setup_msg", description="[ADMIN] Criar mensagem embed personalizada")
@commands.has_permissions(administrator=True)
async def setup_msg_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando admin para criar mensagem embed via modal"""
    try:
        print(f"Comando setup_msg executado por {inter.user.name}")
        
        from utils.ticket_views import SetupMessageModal
        print("SetupMessageModal importado com sucesso!")
        
        modal = SetupMessageModal()
        print("Modal criado com sucesso!")
        
        await inter.response.send_modal(modal)
        print("Modal enviado com sucesso!")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro de importação no sistema de mensagens.",
            color=0x8B5CF6
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Erro no comando setup_msg: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao criar mensagem embed.",
            color=0x8B5CF6
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="setup_suporte", description="[ADMIN] Configurar sistema de tickets de suporte")
@commands.has_permissions(administrator=True)
async def setup_suporte_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando admin para configurar sistema de tickets de suporte via modal"""
    try:
        print(f"Comando setup_suporte executado por {inter.user.name}")
        
        from utils.ticket_views import SetupSupportModal
        print("SetupSupportModal importado com sucesso!")
        
        modal = SetupSupportModal()
        print("Modal de suporte criado com sucesso!")
        
        await inter.response.send_modal(modal)
        print("Modal de suporte enviado com sucesso!")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro de importação no sistema de suporte.",
            color=0x8B5CF6
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Erro no comando setup_suporte: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao configurar sistema de suporte.",
            color=0x8B5CF6
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="set_feedback", description="[ADMIN] Configurar canal de feedback")
@commands.has_permissions(administrator=True)
async def set_feedback_slash(inter: disnake.ApplicationCommandInteraction, canal: disnake.TextChannel):
    """Comando admin para configurar canal de feedback"""
    try:
        print(f"Comando set_feedback executado por {inter.user.name} - Canal: {canal.name}")
        
        from models.guild_config_model import GuildConfigModel
        guild_config = GuildConfigModel()
        
        success = await guild_config.set_feedback_channel(inter.guild_id, canal.id)
        
        if success:
            embed = disnake.Embed(
                title="✅ Canal de Feedback Configurado",
                description=f"Canal de feedback configurado com sucesso!\n\n📢 **Canal:** {canal.mention}",
                color=0x8B5CF6
            )
            embed.add_field(
                name="💡 Como Funciona",
                value="Este canal será mencionado nas mensagens de agradecimento após vendas.",
                inline=False
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(
                description="❌ Erro ao configurar canal de feedback.",
                color=0xFF0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        print(f"Erro no comando set_feedback: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao configurar canal de feedback.",
            color=0xFF0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="set_entregas", description="[ADMIN] Configurar canal de entregas")
@commands.has_permissions(administrator=True)
async def set_entregas_slash(inter: disnake.ApplicationCommandInteraction, canal: disnake.TextChannel):
    """Comando admin para configurar canal de entregas"""
    try:
        print(f"Comando set_entregas executado por {inter.user.name} - Canal: {canal.name}")
        
        from models.guild_config_model import GuildConfigModel
        guild_config = GuildConfigModel()
        
        success = await guild_config.set_deliveries_channel(inter.guild_id, canal.id)
        
        if success:
            embed = disnake.Embed(
                title="✅ Canal de Entregas Configurado",
                description=f"Canal de entregas configurado com sucesso!\n\n📦 **Canal:** {canal.mention}",
                color=0x8B5CF6
            )
            embed.add_field(
                name="💡 Como Funciona",
                value="Este canal será usado para publicar entregas confirmadas (anônimas para gerar autoridade).",
                inline=False
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(
                description="❌ Erro ao configurar canal de entregas.",
                color=0xFF0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        print(f"Erro no comando set_entregas: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao configurar canal de entregas.",
            color=0xFF0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="setlog", description="[ADMIN] Configurar sistema de logs do servidor")
@commands.has_permissions(administrator=True)
async def setlog_slash(inter: disnake.ApplicationCommandInteraction, canal: disnake.TextChannel):
    """Comando admin para configurar logs do servidor"""
    try:
        print(f"Comando setlog executado por {inter.user.name} - Canal: {canal.name}")
        
        # Criar embed explicativo
        embed = disnake.Embed(
            title="📊 Configurar Sistema de Logs",
            description=f"Configure quais eventos você deseja registrar no canal {canal.mention}.",
            color=0x5865F2
        )
        
        embed.add_field(
            name="📋 Como Funciona",
            value="Use o menu abaixo para **selecionar** quais eventos você quer que sejam logados.\n"
                  "Você pode escolher **quantos quiser**!",
            inline=False
        )
        
        embed.add_field(
            name="💡 Presets Recomendados",
            value="🔥 **Apenas Vendas:** payment_confirmed + product_delivered\n"
                  "🎫 **Tickets:** ticket_created + support_ticket_created + ticket_closed\n"
                  "📊 **Completo:** Todos os eventos",
            inline=False
        )
        
        # Importar View com Select Menu
        from utils.log_views import LogEventsSelectView
        view = LogEventsSelectView(canal.id, inter.guild_id)
        
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
        print("View de seleção de eventos enviada com sucesso!")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro de importação no sistema de logs.",
            color=0xFF0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Erro no comando setlog: {e}")
        import traceback
        traceback.print_exc()
        embed = disnake.Embed(
            description="❌ Erro ao configurar sistema de logs.",
            color=0xFF0000
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="setlog", aliases=["configurar_logs", "logs"])
@commands.has_permissions(administrator=True)
async def setlog_prefix(ctx, canal: disnake.TextChannel):
    """Comando prefixado para configurar logs do servidor"""
    try:
        print(f"Comando ?setlog executado por {ctx.author.name} - Canal: {canal.name}")
        
        # Criar embed explicativo
        embed = disnake.Embed(
            title="📊 Configurar Sistema de Logs",
            description=f"Configure quais eventos você deseja registrar no canal {canal.mention}.",
            color=0x5865F2
        )
        
        embed.add_field(
            name="📋 Como Funciona",
            value="Use o menu abaixo para **selecionar** quais eventos você quer que sejam logados.\n"
                  "Você pode escolher **quantos quiser**!",
            inline=False
        )
        
        embed.add_field(
            name="💡 Presets Recomendados",
            value="🔥 **Apenas Vendas:** payment_confirmed + product_delivered\n"
                  "🎫 **Tickets:** ticket_created + support_ticket_created + ticket_closed\n"
                  "📊 **Completo:** Todos os eventos",
            inline=False
        )
        
        # Importar View com Select Menu
        from utils.log_views import LogEventsSelectView
        view = LogEventsSelectView(canal.id, ctx.guild.id)
        
        await ctx.send(embed=embed, view=view)
        print("View de seleção de eventos enviada com sucesso!")
        
    except Exception as e:
        print(f"Erro no comando ?setlog: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send("❌ Erro ao configurar sistema de logs.")

@bot.command(name="clear", aliases=["limpar", "apagar"])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 10):
    """Comando para apagar mensagens do chat
    
    Uso: ?clear [número]
    Exemplo: ?clear 50
    """
    try:
        # Validar o número de mensagens
        if amount < 1:
            await ctx.send("❌ O número deve ser maior que 0!", delete_after=5)
            return
        
        # Apagar mensagens (incluindo o comando)
        # Nota: Discord só permite apagar mensagens com menos de 14 dias em massa
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        # Enviar mensagem de confirmação (que será apagada após 5 segundos)
        confirm_msg = await ctx.send(
            f"🗑️ {len(deleted) - 1} mensagens foram apagadas por {ctx.author.mention}",
            delete_after=5
        )
        
        print(f"✅ {ctx.author.name} apagou {len(deleted) - 1} mensagens em #{ctx.channel.name}")
        
    except disnake.Forbidden:
        await ctx.send("❌ Não tenho permissão para apagar mensagens neste canal!", delete_after=5)
    except disnake.HTTPException as e:
        await ctx.send(f"❌ Erro ao apagar mensagens: {e}", delete_after=5)
    except Exception as e:
        print(f"Erro no comando ?clear: {e}")
        await ctx.send("❌ Ocorreu um erro ao apagar as mensagens.", delete_after=5)

@clear_messages.error
async def clear_error(ctx, error):
    """Handler de erros do comando clear"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando! (Necessário: Gerenciar Mensagens)", delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Uso correto: `?clear [número]` - Exemplo: `?clear 50`", delete_after=5)
    else:
        print(f"Erro no comando clear: {error}")

@bot.slash_command(name="status", description="Ver status do seu pagamento")
async def status_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando para ver status do pagamento"""
    try:
        # Verificar se está em canal de ticket
        if not inter.channel.name.startswith('ticket-'):
            await inter.response.send_message("❌ Este comando só funciona em canais de ticket!", ephemeral=True)
            return
        
        # Buscar transação do usuário neste canal
        transaction_model = TransactionModel()
        transactions = await transaction_model.get_user_transactions(inter.user.id)
        
        # Filtrar pela transação deste canal
        current_transaction = None
        for trans in transactions:
            if trans.get('delivery_channel_id') == inter.channel.id:
                current_transaction = trans
                break
        
        if not current_transaction:
            await inter.response.send_message("❌ Nenhuma transação encontrada neste canal.", ephemeral=True)
            return
        
        # Buscar produto
        product_model = ProductModel()
        product = await product_model.get_product_by_id(current_transaction['product_id'])
        
        status = current_transaction.get('status', 'pending')
        
        # Criar embed baseado no status
        if status == 'pending':
            # Pagamento pendente
            embed = disnake.Embed(
                title="⏳ Pagamento Pendente",
                description=f"Aguardando pagamento do produto **{product['name']}**",
                color=0xffa500
            )
            
            # Calcular tempo restante
            from datetime import datetime
            created_at = datetime.fromisoformat(current_transaction['created_at'].replace('Z', '+00:00'))
            now = datetime.now()
            age_minutes = (now - created_at.replace(tzinfo=None)).total_seconds() / 60
            remaining = max(0, 30 - int(age_minutes))
            
            embed.add_field(
                name="⏱️ Tempo Restante",
                value=f"{remaining} minutos",
                inline=True
            )
            embed.add_field(
                name="💰 Valor",
                value=f"R$ {current_transaction['amount']:.2f}",
                inline=True
            )
            
            # Mostrar QR Code se disponível
            if current_transaction.get('qr_code'):
                embed.add_field(
                    name="🔢 Código Pix",
                    value=f"```{current_transaction['qr_code'][:100]}...```",
                    inline=False
                )
                
                # Gerar QR Code novamente
                import qrcode
                import io
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                qr.add_data(current_transaction['qr_code'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                qr_file = disnake.File(img_bytes, filename="qrcode.png")
                
                await inter.response.send_message(embed=embed, file=qr_file, ephemeral=True)
            else:
                await inter.response.send_message(embed=embed, ephemeral=True)
                
        elif status == 'completed':
            # Pagamento confirmado e produto entregue
            embed = disnake.Embed(
                title="✅ Produto Entregue",
                description=f"Seu pagamento foi confirmado e o produto foi entregue.",
                color=0x00ff00
            )
            embed.add_field(
                name="📦 Produto",
                value=product['name'],
                inline=True
            )
            embed.add_field(
                name="💰 Valor Pago",
                value=f"R$ {current_transaction['amount']:.2f}",
                inline=True
            )
            
            # Buscar item do estoque para reenviar
            from models.inventory_model import InventoryModel
            inventory_model = InventoryModel()
            inventory_item = await inventory_model.get_inventory_by_transaction(current_transaction['id'])
            
            if inventory_item:
                embed.add_field(
                    name="🔑 Seu Produto",
                    value=f"```{inventory_item['content']}```",
                    inline=False
                )
            
            await inter.response.send_message(embed=embed, ephemeral=True)
            
        elif status == 'expired':
            embed = disnake.Embed(
                title="⏰ Pagamento Expirado",
                description=f"O prazo para pagamento expirou.",
                color=0xff0000
            )
            embed.add_field(
                name="💡 Quer tentar novamente?",
                value="Clique no botão 'Criar Ticket' para gerar um novo pagamento.",
                inline=False
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(
                title="📊 Status do Pagamento",
                description=f"Status: **{status}**",
                color=0x3498db
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        print(f"Erro no comando status: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao buscar status do pagamento.", ephemeral=True)

@bot.slash_command(name="comprar", description="Comprar produto do ticket (automático)")
async def comprar_slash(inter: disnake.ApplicationCommandInteraction, produto: str = None):
    """Comando para comprar produto no canal do ticket"""
    try:
        # Verificar se está em canal de ticket
        if not inter.channel.name.startswith('ticket-'):
            await inter.response.send_message("❌ Este comando só funciona em canais de ticket!", ephemeral=True)
            return
        
        # Buscar produto automaticamente do ticket ou pelo nome fornecido
        product_model = ProductModel()
        product = None
        
        # Se produto não foi fornecido, buscar do ticket ativo
        if not produto:
            ticket_data = active_tickets.get(inter.user.id)
            if ticket_data and ticket_data.get('product_id'):
                # Buscar produto pelo ID armazenado no ticket
                product = await product_model.get_product_by_id(ticket_data['product_id'], inter.guild_id)
                print(f"🎯 Produto detectado automaticamente do ticket: {product['name'] if product else 'None'}")
            else:
                await inter.response.send_message(
                    "❌ Não foi possível identificar o produto automaticamente!\n"
                    "💡 Dica: Use `/comprar produto: Nome do Produto`",
                    ephemeral=True
                )
                return
        else:
            # Buscar produto por nome (apenas no servidor atual)
            product = await product_model.get_product_by_name(produto, inter.guild_id)
        
        if not product:
            await inter.response.send_message(
                f"❌ Produto '{produto}' não encontrado neste servidor!" if produto else "❌ Produto não encontrado!",
                ephemeral=True
            )
            return
        
        # Buscar cupom do ticket (se houver)
        coupon_code = None
        coupon_data = None
        discount_amount = 0
        final_amount = product['price']
        split_config = None
        
        # Verificar se tem cupom no ticket
        ticket_data = active_tickets.get(inter.user.id)
        if ticket_data and ticket_data.get('coupon_code'):
            coupon_code = ticket_data['coupon_code']
            
            # Validar cupom (apenas do servidor atual)
            from models.coupon_model import CouponModel
            coupon_model = CouponModel()
            is_valid, message, coupon_data = await coupon_model.validate_coupon(
                coupon_code,
                inter.user.id,
                product['price'],
                inter.guild_id
            )
            
            if is_valid and coupon_data:
                discount_amount = coupon_data['calculated_discount']
                final_amount = coupon_data['calculated_final_amount']
                
                # Verificar se tem split configurado
                if coupon_data.get('split_enabled') and coupon_data.get('split_recipient_id'):
                    split_config = {
                        'recipient_id': coupon_data['split_recipient_id'],
                        'percent': float(coupon_data['split_percent'])
                    }
                
                # Enviar mensagem informando desconto
                await inter.channel.send(
                    f"🎉 Cupom **{coupon_code}** aplicado! Desconto de {coupon_data['discount_percent']}% = R$ {discount_amount:.2f}"
                )
            else:
                # Cupom inválido - informar e continuar sem desconto
                await inter.channel.send(f"⚠️ {message} - Continuando sem desconto.")
                coupon_data = None
        
        # Criar transação
        transaction_model = TransactionModel()
        transaction = await transaction_model.create_transaction(
            user_id=inter.user.id,
            product_id=product['id'],
            amount=product['price'],
            discount_amount=discount_amount,
            final_amount=final_amount,
            coupon_id=coupon_data['id'] if coupon_data else None,
            status='pending'
        )
        
        if not transaction:
            await inter.response.send_message("❌ Erro ao criar transação!", ephemeral=True)
            return
        
        # Gerar pagamento Pix com valor final
        payment_utils = PaymentUtils()
        payment_data = await payment_utils.create_pix_payment(
            amount=final_amount,  # Valor com desconto
            description=f"Compra: {product['name']}",
            customer_email=f"{inter.user.name.lower().replace(' ', '')}@khaos.com",
            customer_name=inter.user.display_name,
            split_config=split_config  # Passar split se houver
        )
        
        if payment_data:
            # Atualizar transação
            await transaction_model.update_transaction(transaction['id'], {
                'payment_id': payment_data.get('id'),
                'pix_code': payment_data.get('pix_code'),
                'qr_code': payment_data.get('qr_code'),
                'email': f"{inter.user.name.lower().replace(' ', '')}@khaos.com"
            })
            
            # Registrar uso do cupom
            if coupon_data:
                from models.coupon_model import CouponModel
                coupon_model = CouponModel()
                await coupon_model.use_coupon(
                    coupon_data['id'],
                    inter.user.id,
                    transaction['id'],
                    discount_amount
                )
            
            # Enviar pagamento
            embed = disnake.Embed(
                title="💳 Pagamento Pix Gerado!",
                description=f"**Produto:** {product['name']}",
                color=0x00ff00
            )
            
            # Mostrar valores com desconto se houver
            if discount_amount > 0:
                embed.add_field(
                    name="💰 Valores",
                    value=f"~~R$ {product['price']:.2f}~~ → **R$ {final_amount:.2f}**\n🎟️ Desconto: R$ {discount_amount:.2f}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="💰 Valor",
                    value=f"R$ {final_amount:.2f}",
                    inline=False
                )
            
            embed.add_field(
                name="📱 QR Code",
                value="Escaneie o QR Code abaixo com seu app de pagamento:",
                inline=False
            )
            
            embed.add_field(
                name="🔢 Código Pix",
                value=f"```{payment_data.get('pix_code', 'N/A')}```",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Validade",
                value="⏱️ **30 minutos** para efetuar o pagamento",
                inline=False
            )
            
            embed.set_footer(text=f"ID da Transação: {transaction['id']}")
            
            await inter.response.send_message(embed=embed)
            
            # Gerar e enviar QR Code como imagem
            try:
                import qrcode
                import io
                
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4
                )
                qr.add_data(payment_data.get('pix_code'))
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                await inter.channel.send(
                    content=f"{inter.user.mention} 📱 **QR Code do Pagamento**",
                    file=disnake.File(img_buffer, filename='qrcode_pix.png')
                )
            except Exception as qr_error:
                print(f"Erro ao gerar QR Code: {qr_error}")
            
            # Atualizar dados do ticket
            if inter.user.id in active_tickets:
                active_tickets[inter.user.id]['transaction_id'] = transaction['id']
                active_tickets[inter.user.id]['product'] = product
            
            # Salvar canal de entrega na transação
            await transaction_model.update_transaction(transaction['id'], {
                'delivery_channel_id': inter.channel.id
            })
            
        else:
            await inter.response.send_message("❌ Erro ao gerar pagamento Pix!", ephemeral=True)
            
    except Exception as e:
        print(f"Erro no comando comprar: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao processar compra!", ephemeral=True)

@bot.slash_command(name="ajuda", description="Exibe a lista de comandos disponíveis")
async def ajuda_slash(inter: disnake.ApplicationCommandInteraction):
    """Exibe a lista de comandos disponíveis"""
    embed = disnake.Embed(
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
        value="`/ajuda` :: 🤖 Lista de comandos\n`/produtos` :: 🛍️ Ver produtos disponíveis\n`/comprar` :: 💳 Gerar pagamento (detecta automaticamente!)\n`/status` :: 📊 Status do pagamento",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos Admin",
        value="`/setup_ticket` :: ⚙️ Enviar mensagem de tickets (vendas)\n`/setup_suporte` :: 🆘 Enviar mensagem de suporte\n`/setup_msg` :: 📝 Criar mensagem embed\n`/close_ticket` :: 🔒 Fechar ticket manualmente\n`?clear [número]` :: 🗑️ Apagar mensagens do chat",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos de Estoque (Admin)",
        value="`/adicionar_estoque` :: 📦 Adicionar códigos/keys\n`/ver_estoque` :: 📊 Ver resumo do estoque\n`?adicionar_estoque` :: 📦 Adicionar via prefixo\n`?ver_estoque` :: 📊 Ver estoque via prefixo",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos de Cupons (Admin)",
        value="`/criar_cupom` :: 🎟️ Criar novo cupom\n`/listar_cupons` :: 📋 Ver todos cupons\n`/cupom_stats` :: 📊 Estatísticas de cupom\n`/deletar_cupom` :: ❌ Desativar cupom",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos VIP",
        value="`/meu_vip` :: 👑 Ver sua assinatura VIP\n`/renovar_vip` :: 🔄 Ver planos disponíveis\n`/historico_vip` :: 📋 Histórico de assinaturas",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos VIP (Admin)",
        value="`/listar_vips` :: 📋 Listar VIPs ativos\n`/adicionar_vip` :: ➕ Adicionar VIP manual\n`/remover_vip` :: ➖ Remover VIP\n`/vip_stats` :: 📊 Estatísticas VIP",
        inline=False
    )
    
    embed.add_field(
        name="» Sistema de Pagamento",
        value="💎 **Pix Instantâneo** - QR Code + Código\n🚀 **Entrega Automática** - Após confirmação\n🛡️ **Suporte 24/7** - Atendimento completo",
        inline=False
    )
    
    embed.set_footer(text="Sistema de vendas automatizado • Powered by Khaos")
    
    side_embed = disnake.Embed(
        description="📋 Lista de comandos disponíveis:",
        color=0x8B5CF6
    )
    
    await inter.response.send_message(embeds=[embed, side_embed])

# ========================================
# COMANDOS DE CUPONS (ADMIN)
# ========================================

@bot.slash_command(name="criar_cupom", description="[ADMIN] Criar novo cupom de desconto")
@commands.has_permissions(administrator=True)
async def criar_cupom_slash(inter: disnake.ApplicationCommandInteraction):
    """Comando admin para criar cupom via modal"""
    try:
        from utils.ticket_views import CreateCouponModal
        
        modal = CreateCouponModal()
        await inter.response.send_modal(modal)
        
    except Exception as e:
        print(f"Erro no comando criar_cupom: {e}")
        await inter.response.send_message("❌ Erro ao abrir modal de cupom.", ephemeral=True)

@bot.slash_command(name="listar_cupons", description="[ADMIN] Listar todos os cupons")
@commands.has_permissions(administrator=True)
async def listar_cupons_slash(inter: disnake.ApplicationCommandInteraction):
    """Lista todos os cupons ativos"""
    try:
        from models.coupon_model import CouponModel
        
        coupon_model = CouponModel()
        coupons = await coupon_model.get_all_coupons(inter.guild_id, active_only=True)
        
        if not coupons:
            await inter.response.send_message("📋 Nenhum cupom cadastrado.", ephemeral=True)
            return
        
        embed = disnake.Embed(
            title="🎟️ Cupons Cadastrados",
            description=f"Total: {len(coupons)} cupons ativos",
            color=0x8B5CF6
        )
        
        for coupon in coupons[:10]:  # Mostrar no máximo 10
            uses_info = f"{coupon.get('uses_count', 0)}"
            if coupon.get('max_uses'):
                uses_info += f"/{coupon['max_uses']}"
            else:
                uses_info += " (ilimitado)"
            
            value = f"**Desconto:** {coupon['discount_percent']}%\n"
            value += f"**Usos:** {uses_info}\n"
            value += f"**Um por usuário:** {'Sim' if coupon.get('one_per_user') else 'Não'}"
            
            if coupon.get('expires_at'):
                from datetime import datetime
                expires = datetime.fromisoformat(coupon['expires_at'].replace('Z', '+00:00'))
                value += f"\n**Expira:** {expires.strftime('%d/%m/%Y')}"
            
            embed.add_field(
                name=f"🎫 {coupon['code']}",
                value=value,
                inline=True
            )
        
        if len(coupons) > 10:
            embed.set_footer(text=f"Mostrando 10 de {len(coupons)} cupons")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando listar_cupons: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao listar cupons.", ephemeral=True)

@bot.slash_command(name="cupom_stats", description="[ADMIN] Ver estatísticas de um cupom")
@commands.has_permissions(administrator=True)
async def cupom_stats_slash(inter: disnake.ApplicationCommandInteraction, codigo: str):
    """Mostra estatísticas de uso de um cupom"""
    try:
        from models.coupon_model import CouponModel
        
        coupon_model = CouponModel()
        stats = await coupon_model.get_coupon_stats(codigo, inter.guild_id)
        
        if not stats:
            await inter.response.send_message(f"❌ Cupom '{codigo}' não encontrado neste servidor.", ephemeral=True)
            return
        
        coupon = stats['coupon']
        
        embed = disnake.Embed(
            title=f"📊 Estatísticas: {coupon['code']}",
            description=f"Desconto de {coupon['discount_percent']}%",
            color=0x00ff00
        )
        
        # Informações gerais
        embed.add_field(
            name="📈 Uso Total",
            value=str(stats['total_uses']),
            inline=True
        )
        
        embed.add_field(
            name="💰 Desconto Total Aplicado",
            value=f"R$ {stats['total_discount']:.2f}",
            inline=True
        )
        
        limit_info = str(coupon.get('max_uses')) if coupon.get('max_uses') else "Ilimitado"
        embed.add_field(
            name="🎯 Limite",
            value=limit_info,
            inline=True
        )
        
        # Usuários recentes
        if stats['recent_users']:
            users_text = "\n".join([f"<@{user_id}>" for user_id in stats['recent_users'][:5]])
            embed.add_field(
                name="👥 Últimos Usuários",
                value=users_text,
                inline=False
            )
        
        # Informações adicionais
        extra_info = f"**Um por usuário:** {'Sim' if coupon.get('one_per_user') else 'Não'}\n"
        extra_info += f"**Status:** {'Ativo' if coupon.get('active') else 'Inativo'}"
        
        if coupon.get('expires_at'):
            from datetime import datetime
            expires = datetime.fromisoformat(coupon['expires_at'].replace('Z', '+00:00'))
            extra_info += f"\n**Expira:** {expires.strftime('%d/%m/%Y')}"
        
        embed.add_field(
            name="ℹ️ Informações",
            value=extra_info,
            inline=False
        )
        
        embed.set_footer(text=f"Criado por: {coupon.get('created_by', 'N/A')}")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando cupom_stats: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao buscar estatísticas.", ephemeral=True)

@bot.slash_command(name="deletar_cupom", description="[ADMIN] Desativar um cupom")
@commands.has_permissions(administrator=True)
async def deletar_cupom_slash(inter: disnake.ApplicationCommandInteraction, codigo: str):
    """Desativa um cupom"""
    try:
        from models.coupon_model import CouponModel
        
        coupon_model = CouponModel()
        success, message = await coupon_model.delete_cupom(codigo)
        
        if success:
            embed = disnake.Embed(
                title="✅ Cupom Desativado",
                description=message,
                color=0x00ff00
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            await inter.response.send_message(f"❌ {message}", ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando deletar_cupom: {e}")
        await inter.response.send_message("❌ Erro ao deletar cupom.", ephemeral=True)

# ========================================
# COMANDOS VIP (USUÁRIO)
# ========================================

@bot.slash_command(name="meu_vip", description="Ver status da sua assinatura VIP")
async def meu_vip_slash(inter: disnake.ApplicationCommandInteraction):
    """Mostra informações da assinatura VIP do usuário"""
    try:
        from models.vip_model import VipModel
        from datetime import datetime
        
        vip_model = VipModel()
        subscription = await vip_model.get_user_subscription(
            inter.user.id,
            inter.guild.id
        )
        
        if not subscription:
            embed = disnake.Embed(
                title="❌ Você não é VIP",
                description="Você não possui uma assinatura VIP ativa no momento.",
                color=disnake.Color.red()
            )
            embed.add_field(
                name="💎 Quer se tornar VIP?",
                value="Use `/renovar_vip` para ver os planos disponíveis!",
                inline=False
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Calcular informações
        started_at = datetime.fromisoformat(subscription['started_at'].replace('Z', '+00:00'))
        
        embed = disnake.Embed(
            title="👑 Sua Assinatura VIP",
            description=f"Olá {inter.user.mention}! Aqui estão os detalhes da sua assinatura VIP.",
            color=disnake.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🏆 Role VIP",
            value=f"**{subscription['role_name']}**",
            inline=True
        )
        
        # Informações de duração e expiração
        if subscription['duration_days'] is None:
            status_text = "🌟 **VITALÍCIO**\nSua assinatura nunca expira!"
        else:
            expires_at = datetime.fromisoformat(subscription['expires_at'].replace('Z', '+00:00'))
            days_left = (expires_at.replace(tzinfo=None) - datetime.now()).days
            
            if days_left <= 3:
                status_emoji = "⚠️"
            else:
                status_emoji = "✅"
            
            status_text = f"{status_emoji} **{days_left} dia(s) restante(s)**\nExpira: <t:{int(expires_at.timestamp())}:R>"
        
        embed.add_field(
            name="📅 Status",
            value=status_text,
            inline=True
        )
        
        embed.add_field(
            name="📆 Início",
            value=f"<t:{int(started_at.timestamp())}:F>",
            inline=False
        )
        
        embed.add_field(
            name="✨ Benefícios Ativos",
            value="• Acesso a canais exclusivos VIP\n"
                  "• Prioridade no suporte\n"
                  "• Descontos especiais\n"
                  "• Conteúdo exclusivo",
            inline=False
        )
        
        if subscription['duration_days'] is not None:
            embed.add_field(
                name="🔄 Renovação",
                value="Use `/renovar_vip` para renovar sua assinatura!",
                inline=False
            )
        
        embed.set_footer(
            text=f"VIP desde {started_at.strftime('%d/%m/%Y')}",
            icon_url=inter.user.display_avatar.url if inter.user.display_avatar else None
        )
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando meu_vip: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao buscar informações VIP.", ephemeral=True)

@bot.slash_command(name="renovar_vip", description="Ver planos VIP disponíveis para renovação")
async def renovar_vip_slash(inter: disnake.ApplicationCommandInteraction):
    """Mostra os planos VIP disponíveis"""
    try:
        from models.product_model import ProductModel
        
        product_model = ProductModel()
        all_products = await product_model.get_products_by_guild(inter.guild_id)
        
        # Filtrar apenas produtos VIP
        vip_products = [p for p in all_products if p.get('category') == 'VIP']
        
        if not vip_products:
            await inter.response.send_message("❌ Nenhum plano VIP disponível no momento.", ephemeral=True)
            return
        
        embed = disnake.Embed(
            title="👑 Planos VIP Disponíveis",
            description="Escolha o plano que mais combina com você e aproveite todos os benefícios exclusivos!",
            color=disnake.Color.gold()
        )
        
        # Agrupar por role
        by_role = {}
        for product in vip_products:
            vip_config = product.get('vip_config', {})
            role_name = vip_config.get('role_name', 'VIP')
            
            if role_name not in by_role:
                by_role[role_name] = []
            by_role[role_name].append(product)
        
        # Adicionar campos por role
        for role_name, products in by_role.items():
            products_text = ""
            
            for product in products:
                vip_config = product.get('vip_config', {})
                duration = vip_config.get('duration_days')
                
                if duration is None:
                    duration_text = "🌟 Vitalício"
                elif duration == 1:
                    duration_text = "⏰ 1 dia"
                else:
                    duration_text = f"⏰ {duration} dias"
                
                products_text += f"**{product['name']}**\n{duration_text} - R$ {product['price']:.2f}\n\n"
            
            embed.add_field(
                name=f"👑 {role_name}",
                value=products_text.strip(),
                inline=True
            )
        
        embed.add_field(
            name="✨ Benefícios VIP",
            value="• Acesso a canais exclusivos\n"
                  "• Prioridade no suporte\n"
                  "• Descontos especiais\n"
                  "• Conteúdo exclusivo\n"
                  "• E muito mais!",
            inline=False
        )
        
        embed.add_field(
            name="🛒 Como Comprar",
            value="1. Crie um ticket de compra\n"
                  "2. Use `/comprar [nome do produto VIP]`\n"
                  "3. Pague via Pix\n"
                  "4. Receba sua role automaticamente!",
            inline=False
        )
        
        embed.set_footer(text="Invista no seu futuro VIP! 💎")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando renovar_vip: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao carregar planos VIP.", ephemeral=True)

@bot.slash_command(name="historico_vip", description="Ver histórico de assinaturas VIP")
async def historico_vip_slash(inter: disnake.ApplicationCommandInteraction):
    """Mostra o histórico completo de assinaturas VIP do usuário"""
    try:
        from models.vip_model import VipModel
        from datetime import datetime
        
        vip_model = VipModel()
        history = await vip_model.get_subscription_history(
            inter.user.id,
            inter.guild.id
        )
        
        if not history:
            embed = disnake.Embed(
                title="📋 Histórico VIP",
                description="Você ainda não possui histórico de assinaturas VIP.",
                color=disnake.Color.blue()
            )
            embed.add_field(
                name="💎 Quer se tornar VIP?",
                value="Use `/renovar_vip` para ver os planos disponíveis!",
                inline=False
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = disnake.Embed(
            title="📋 Seu Histórico VIP",
            description=f"Histórico completo de assinaturas de {inter.user.mention}",
            color=disnake.Color.blue(),
            timestamp=datetime.now()
        )
        
        for i, sub in enumerate(history[:10], 1):  # Limitar a 10
            status_emoji = {
                'active': '✅',
                'expired': '⏰',
                'cancelled': '🚫'
            }.get(sub['status'], '❓')
            
            started = datetime.fromisoformat(sub['started_at'].replace('Z', '+00:00'))
            
            value_text = f"**Status:** {status_emoji} {sub['status'].upper()}\n"
            value_text += f"**Início:** <t:{int(started.timestamp())}:d>\n"
            
            if sub['duration_days'] is None:
                value_text += "**Duração:** 🌟 Vitalício"
            else:
                value_text += f"**Duração:** {sub['duration_days']} dias"
            
            if sub['expires_at']:
                expires = datetime.fromisoformat(sub['expires_at'].replace('Z', '+00:00'))
                value_text += f"\n**Expirou:** <t:{int(expires.timestamp())}:d>"
            
            embed.add_field(
                name=f"{i}. {sub['role_name']}",
                value=value_text,
                inline=True
            )
        
        if len(history) > 10:
            embed.set_footer(text=f"Mostrando 10 de {len(history)} assinaturas")
        else:
            embed.set_footer(text=f"Total: {len(history)} assinatura(s)")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando historico_vip: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao buscar histórico VIP.", ephemeral=True)

# ========================================
# COMANDOS VIP (ADMIN)
# ========================================

@bot.slash_command(name="listar_vips", description="[ADMIN] Listar todos os VIPs ativos do servidor")
@commands.has_permissions(administrator=True)
async def listar_vips_slash(inter: disnake.ApplicationCommandInteraction):
    """Lista todos os membros VIP ativos"""
    try:
        from models.vip_model import VipModel
        from datetime import datetime
        
        vip_model = VipModel()
        subscriptions = await vip_model.get_all_subscriptions(
            inter.guild.id,
            status='active'
        )
        
        if not subscriptions:
            await inter.response.send_message("📋 Nenhum VIP ativo no servidor.", ephemeral=True)
            return
        
        embed = disnake.Embed(
            title="👑 VIPs Ativos do Servidor",
            description=f"Total: {len(subscriptions)} membro(s) VIP ativo(s)",
            color=disnake.Color.gold(),
            timestamp=datetime.now()
        )
        
        # Agrupar por role
        by_role = {}
        for sub in subscriptions:
            role_name = sub['role_name']
            if role_name not in by_role:
                by_role[role_name] = []
            by_role[role_name].append(sub)
        
        # Adicionar campos por role
        for role_name, subs in by_role.items():
            users_text = ""
            
            for sub in subs[:10]:  # Limitar 10 por role
                user = inter.guild.get_member(sub['user_id'])
                user_mention = user.mention if user else f"ID: {sub['user_id']}"
                
                if sub['duration_days'] is None:
                    duration_text = "🌟 Vitalício"
                else:
                    expires_at = datetime.fromisoformat(sub['expires_at'].replace('Z', '+00:00'))
                    days_left = (expires_at.replace(tzinfo=None) - datetime.now()).days
                    duration_text = f"⏰ {days_left}d"
                
                users_text += f"{user_mention} - {duration_text}\n"
            
            if len(subs) > 10:
                users_text += f"\n*...e mais {len(subs) - 10}*"
            
            embed.add_field(
                name=f"👑 {role_name} ({len(subs)})",
                value=users_text.strip(),
                inline=False
            )
        
        embed.set_footer(text="Use /vip_stats para ver estatísticas completas")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando listar_vips: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao listar VIPs.", ephemeral=True)

@bot.slash_command(name="adicionar_vip", description="[ADMIN] Adicionar VIP manualmente a um usuário")
@commands.has_permissions(administrator=True)
async def adicionar_vip_slash(
    ctx: disnake.ApplicationCommandInteraction,
    membro: disnake.Member,
    role_vip: str,
    duracao_dias: int = None
):
    """Adiciona VIP manualmente a um usuário"""
    try:
        from models.vip_model import VipModel
        from utils.vip_manager import VipManager
        
        vip_manager = VipManager(bot)
        vip_model = VipModel()
        
        # Adicionar role
        role = await vip_manager.grant_vip_role(membro, role_vip)
        if not role:
            await ctx.response.send_message(
                f"❌ Erro ao adicionar role {role_vip}. Verifique se o bot tem permissões adequadas.",
                ephemeral=True
            )
            return
        
        # Criar assinatura no banco
        subscription = await vip_model.create_subscription(
            user_id=membro.id,
            guild_id=ctx.guild.id,
            role_id=role.id,
            role_name=role_vip,
            product_id=0,  # 0 indica adição manual
            duration_days=duracao_dias,
            transaction_id=None
        )
        
        if not subscription:
            await ctx.response.send_message("❌ Erro ao criar assinatura no banco.", ephemeral=True)
            return
        
        # Criar embed de confirmação
        embed = disnake.Embed(
            title="✅ VIP Adicionado Manualmente",
            description=f"VIP adicionado com sucesso para {membro.mention}",
            color=disnake.Color.green()
        )
        
        embed.add_field(
            name="👑 Role",
            value=role_vip,
            inline=True
        )
        
        if duracao_dias is None:
            duration_text = "🌟 Vitalício"
        else:
            duration_text = f"⏰ {duracao_dias} dias"
        
        embed.add_field(
            name="📅 Duração",
            value=duration_text,
            inline=True
        )
        
        embed.add_field(
            name="👤 Admin",
            value=ctx.user.mention,
            inline=True
        )
        
        await ctx.response.send_message(embed=embed, ephemeral=True)
        
        # Enviar DM para o usuário (criar produto fictício para a mensagem)
        fake_product = {
            'id': 0,
            'name': f"{role_vip} - Manual",
            'description': "Adicionado manualmente pela administração"
        }
        await vip_manager.send_vip_welcome_dm(membro, subscription, fake_product)
        
    except Exception as e:
        print(f"Erro no comando adicionar_vip: {e}")
        import traceback
        traceback.print_exc()
        await ctx.response.send_message("❌ Erro ao adicionar VIP.", ephemeral=True)

@bot.slash_command(name="remover_vip", description="[ADMIN] Remover VIP de um usuário")
@commands.has_permissions(administrator=True)
async def remover_vip_slash(inter: disnake.ApplicationCommandInteraction, membro: disnake.Member):
    """Remove VIP de um usuário"""
    try:
        from models.vip_model import VipModel
        from utils.vip_manager import VipManager
        
        vip_model = VipModel()
        vip_manager = VipManager(bot)
        
        # Buscar assinatura ativa
        subscription = await vip_model.get_user_subscription(
            membro.id,
            inter.guild.id
        )
        
        if not subscription:
            await inter.response.send_message(
                f"❌ {membro.mention} não possui VIP ativo.",
                ephemeral=True
            )
            return
        
        # Cancelar assinatura
        await vip_model.cancel_subscription(subscription['id'])
        
        # Remover role
        await vip_manager.remove_vip_role(subscription)
        
        embed = disnake.Embed(
            title="🚫 VIP Removido",
            description=f"VIP removido de {membro.mention}",
            color=disnake.Color.orange()
        )
        
        embed.add_field(
            name="👑 Role Removida",
            value=subscription['role_name'],
            inline=True
        )
        
        embed.add_field(
            name="👤 Admin",
            value=inter.user.mention,
            inline=True
        )
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando remover_vip: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao remover VIP.", ephemeral=True)

@bot.slash_command(name="vip_stats", description="[ADMIN] Ver estatísticas de VIPs do servidor")
@commands.has_permissions(administrator=True)
async def vip_stats_slash(inter: disnake.ApplicationCommandInteraction):
    """Mostra estatísticas detalhadas dos VIPs"""
    try:
        from models.vip_model import VipModel
        
        vip_model = VipModel()
        stats = await vip_model.get_vip_stats(inter.guild.id)
        
        embed = disnake.Embed(
            title="📊 Estatísticas VIP do Servidor",
            description=f"Estatísticas completas de assinaturas VIP",
            color=disnake.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="✅ VIPs Ativos",
            value=str(stats['total_active']),
            inline=True
        )
        
        embed.add_field(
            name="⏰ VIPs Expirados",
            value=str(stats['total_expired']),
            inline=True
        )
        
        embed.add_field(
            name="🌟 Vitalícios",
            value=str(stats['vitalicio_count']),
            inline=True
        )
        
        # Distribuição por role
        if stats['by_role']:
            roles_text = ""
            for role_name, count in stats['by_role'].items():
                roles_text += f"**{role_name}:** {count}\n"
            
            embed.add_field(
                name="👑 Distribuição por Role",
                value=roles_text.strip(),
                inline=False
            )
        
        embed.set_footer(text="Use /listar_vips para ver a lista completa")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando vip_stats: {e}")
        import traceback
        traceback.print_exc()
        await inter.response.send_message("❌ Erro ao buscar estatísticas VIP.", ephemeral=True)

# ========================================
# COMANDOS DE PRODUTOS
# ========================================

@bot.slash_command(name="produtos", description="Ver produtos disponíveis")
async def produtos_slash(inter: disnake.ApplicationCommandInteraction):
    """Exibe os produtos disponíveis via slash command"""
    try:
        products = await product_model.get_products_by_guild(inter.guild_id)
        
        if not products:
            embed = disnake.Embed(
                description="❌ Nenhum produto disponível no momento.",
                color=0x8B5CF6
            )
            await inter.response.send_message(embed=embed)
            return
        
        # Criar embed principal
        embed = disnake.Embed(
            title="🛍️ Loja Digital Khaos",
            description="**Produtos digitais premium com entrega instantânea!**\n\n💎 **Pagamento via Pix** • 🚀 **Entrega automática** • 🛡️ **Garantia total**",
            color=0x8B5CF6
        )
        
        # Agrupar produtos por categoria
        categories = {}
        for product in products:
            category = product.get('category', 'Outros')
            if category not in categories:
                categories[category] = []
            categories[category].append(product)
        
        # Adicionar produtos por categoria
        for category, category_products in categories.items():
            category_emoji = {
                "Jogos Digitais": "🎮",
                "Streaming": "📺", 
                "Gaming": "🎯",
                "Software": "💻",
                "Outros": "📦"
            }.get(category, "📦")
            
            products_text = ""
            for product in category_products:
                products_text += f"**{product['name']}** - R$ {product['price']:.2f}\n"
                products_text += f"*{product['description'][:80]}...*\n\n"
            
            embed.add_field(
                name=f"{category_emoji} {category}",
                value=products_text.strip(),
                inline=False
            )
        
        embed.add_field(
            name="🛒 Como Comprar",
            value="1️⃣ Use `/setup_ticket` para criar botão de compra\n2️⃣ Clique em \"Criar Ticket de Compra\"\n3️⃣ Escolha seu produto no modal\n4️⃣ Use `/comprar` no canal privado",
            inline=False
        )
        
        embed.set_footer(text=f"📊 {len(products)} produtos disponíveis • Powered by Khaos")
        
        await inter.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando /produtos: {e}")
        embed = disnake.Embed(
            description="❌ Erro ao carregar produtos. Tente novamente em alguns instantes.",
            color=0x8B5CF6
        )
        await inter.response.send_message(embed=embed)

# Inicializar modelos
product_model = ProductModel()
transaction_model = TransactionModel()
payment_utils = PaymentUtils()
# ticket_manager será inicializado após o bot estar pronto

# Dicionário para armazenar tickets ativos
active_tickets = {}

# Função auxiliar para responder comandos
async def respond_command(ctx, message, embed=None, ephemeral=False):
    """Responde comandos tanto slash quanto prefixo"""
    if hasattr(ctx, 'interaction') and ctx.interaction:
        if embed:
            await ctx.interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            await ctx.interaction.response.send_message(message, ephemeral=ephemeral)
    else:
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(message)

async def respond_with_side_embed(ctx, message, embed=None, ephemeral=False):
    """Responde apenas com embed lateral roxo"""
    # Criar embed lateral roxo simples apenas com a mensagem
    side_embed = disnake.Embed(
        description=message,
        color=0x8B5CF6  # Roxo
    )
    
    # Se já tem um embed principal, enviar apenas ambos embeds
    if embed:
        if hasattr(ctx, 'interaction') and ctx.interaction:
            await ctx.interaction.response.send_message(embeds=[embed, side_embed], ephemeral=ephemeral)
        else:
            await ctx.send(embeds=[embed, side_embed])
    else:
        # Se não tem embed principal, enviar apenas embed lateral
        if hasattr(ctx, 'interaction') and ctx.interaction:
            await ctx.interaction.response.send_message(embed=side_embed, ephemeral=ephemeral)
        else:
            await ctx.send(embed=side_embed)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    print(f'ID: {bot.user.id}')
    print(f'Guilds: {len(bot.guilds)}')
    
    # Inicializar sistema de logs
    bot.log_system = LogSystem(bot)
    print("✅ Sistema de logs inicializado")
    
    # Inicializar ticket manager com bot
    global ticket_manager
    ticket_manager = TicketManager(bot)
    print("✅ Ticket Manager inicializado")
    
    # Listar guilds conectadas
    for guild in bot.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")
    
    # Sincronizar comandos slash
    try:
        print("🔄 Sincronizando comandos slash...")
        
        # Aguardar um pouco para garantir que o bot está totalmente conectado
        await asyncio.sleep(2)
        
        # Listar comandos registrados antes da sincronização
        slash_cmds = getattr(bot, 'pending_application_commands', list(bot.application_commands))
        prefix_cmds = list(bot.all_commands.keys())
        
        print(f"📋 Slash commands: {len(slash_cmds)}")
        for cmd in slash_cmds:
            print(f"  - /{cmd.name}: {cmd.description}")
            
        print(f"📋 Prefix commands (?): {len(prefix_cmds)}")
        for cmd_name in prefix_cmds:
            cmd = bot.all_commands[cmd_name]
            # Verificar se é um Command (prefix) ou SlashCommand
            if hasattr(cmd, 'help'):
                print(f"  - ?{cmd_name}: {cmd.help or 'Sem descrição'}")
            else:
                # Se não tiver help (é um SlashCommand), pegar a description
                desc = getattr(cmd, 'description', 'Sem descrição')
                print(f"  - ?{cmd_name}: {desc}")
        
        # Tentar sincronizar globalmente
        try:
            print("🌍 Tentando sincronização global...")
            # Em disnake, sync_commands é um método estático
            if hasattr(bot, 'sync_all_commands'):
                synced = await bot.sync_all_commands()
                print(f"✅ Comandos sincronizados usando sync_all_commands!")
            else:
                # Fallback: tentar await para sincronização automática
                print("⚠️ sync_all_commands não disponível, usando sincronização automática")
            
            # Aguardar um pouco para a sincronização se propagar
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"❌ Erro na sincronização global: {e}")
            print("🏠 Tentando sincronização por guild...")
            
            # Tentar sincronizar por guild
            for guild in bot.guilds:
                try:
                    print(f"🔄 Sincronizando na guild: {guild.name} (ID: {guild.id})")
                    # Em disnake, use bot.sync_commands_force() com guild_id
                    if hasattr(bot, 'sync_commands_force'):
                        synced = await bot.sync_commands_force([guild.id])
                        print(f"✅ Comandos sincronizados na guild {guild.name} usando sync_commands_force!")
                    else:
                        print(f"⚠️ sync_commands_force não disponível")
                    
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
            app_commands = getattr(bot, 'pending_application_commands', list(bot.application_commands))
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
    # DESABILITADO - Agora temos multi-servidor com produtos por guild
    # await load_sample_products()
    
    # Inicializar inventory model
    from models.inventory_model import InventoryModel
    inventory_model = InventoryModel()
    await inventory_model.initialize()
    
    # Inicializar VIP model
    from models.vip_model import VipModel
    vip_model = VipModel()
    await vip_model.initialize()
    
    # Iniciar webhook server
    try:
        from utils.webhook_handler import WebhookHandler
        webhook_port = int(os.getenv('WEBHOOK_PORT', '8080'))
        bot.webhook_handler = WebhookHandler(bot, port=webhook_port)
        asyncio.create_task(bot.webhook_handler.start())
    except Exception as e:
        print(f"⚠️ Erro ao iniciar webhook server: {e}")
    
    # Iniciar payment checker (polling)
    try:
        from utils.payment_checker import PaymentChecker
        bot.payment_checker = PaymentChecker(bot)
        asyncio.create_task(bot.payment_checker.start_checking())
    except Exception as e:
        print(f"⚠️ Erro ao iniciar payment checker: {e}")
    
    # Iniciar task para liberar reservas expiradas
    from disnake.ext import tasks
    
    @tasks.loop(minutes=5)
    async def release_expired_reservations():
        """Libera reservas de estoque expiradas a cada 5 minutos"""
        try:
            released = await inventory_model.release_expired_reservations()
            if released > 0:
                print(f"🔓 {released} reservas expiradas foram liberadas")
        except Exception as e:
            print(f"❌ Erro ao liberar reservas: {e}")
    
    release_expired_reservations.start()
    
    # Iniciar task para verificar assinaturas VIP
    @tasks.loop(hours=6)
    async def check_vip_expirations():
        """Verifica assinaturas VIP expiradas e próximas de expirar a cada 6 horas"""
        try:
            from utils.vip_manager import VipManager
            vip_manager = VipManager(bot)
            
            # 1. Expirar assinaturas vencidas
            expired = await vip_model.check_and_expire_subscriptions()
            for sub in expired:
                # Remover role
                await vip_manager.remove_vip_role(sub)
                # Notificar usuário
                await vip_manager.send_vip_expired_dm(sub)
            
            # 2. Avisar assinaturas próximas de expirar (3 dias)
            expiring = await vip_model.get_expiring_subscriptions(days=3)
            for sub in expiring:
                # Verificar se já foi avisado (implementar controle depois se necessário)
                await vip_manager.send_vip_expiration_warning(sub)
            
            if expired or expiring:
                print(f"👑 VIP Check: {len(expired)} expirado(s), {len(expiring)} próximo(s) de expirar")
                
        except Exception as e:
            print(f"❌ Erro ao verificar expirações VIP: {e}")
            import traceback
            traceback.print_exc()
    
    check_vip_expirations.start()
    
    # Carregar comandos de admin
    try:
        from commands.admin_commands import setup_admin_commands
        await setup_admin_commands(bot)
    except Exception as e:
        print(f"⚠️ Erro ao carregar comandos de admin: {e}")
        import traceback
        traceback.print_exc()
    
    # Adicionar view persistente para tickets
    bot.add_view(TicketView())
    bot.add_view(TicketChannelView())
    
    print("✅ Bot inicializado com sistema de tickets e entrega automática!")

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
    
    # Se existem produtos antigos, vamos substituí-los pelos novos
    if products:
        print("🔄 Produtos antigos encontrados. Substituindo pelos novos produtos digitais...")
        # Limpar produtos antigos
        for product in products:
            await product_model.delete_product(product['id'])
        print("✅ Produtos antigos removidos")
    
    # Carregar novos produtos digitais
    sample_products = [
        {
            "name": "Minecraft Premium",
            "description": "Conta Minecraft Premium original com acesso completo ao jogo. Inclui skin personalizada e histórico limpo.",
            "price": 10.00,
            "category": "Jogos Digitais"
        },
        {
            "name": "Spotify Premium",
            "description": "Conta Spotify Premium válida por 3 meses. Música sem anúncios, download offline e qualidade máxima.",
            "price": 10.00,
            "category": "Streaming"
        },
        {
            "name": "Netflix Premium",
            "description": "Conta Netflix Premium compartilhada por 1 mês. Acesso completo a todos os conteúdos em 4K.",
            "price": 10.00,
            "category": "Streaming"
        },
        {
            "name": "Discord Nitro",
            "description": "Discord Nitro válido por 1 mês. Uploads maiores, emojis personalizados e boost de servidor.",
            "price": 10.00,
            "category": "Gaming"
        },
        {
            "name": "Adobe Creative Cloud",
            "description": "Acesso completo ao Adobe Creative Cloud por 1 mês. Photoshop, Illustrator, Premiere Pro e mais.",
            "price": 10.00,
            "category": "Software"
        },
        {
            "name": "Office 365",
            "description": "Microsoft Office 365 válido por 1 ano. Word, Excel, PowerPoint e OneDrive com 1TB.",
            "price": 10.00,
            "category": "Software"
        },
        {
            "name": "Steam Wallet",
            "description": "Saldo Steam Wallet de R$ 50,00. Use para comprar jogos, DLCs e itens na Steam.",
            "price": 10.00,
            "category": "Gaming"
        },
        {
            "name": "YouTube Premium",
            "description": "YouTube Premium por 3 meses. Sem anúncios, downloads offline e YouTube Music incluído.",
            "price": 10.00,
            "category": "Streaming"
        },
        # Produtos VIP
        {
            "name": "VIP Bronze - 1 Dia",
            "description": "Acesso VIP Bronze por 1 dia. Experimente todos os benefícios exclusivos!",
            "price": 5.00,
            "category": "VIP",
            "vip_config": {
                "role_name": "VIP Bronze",
                "duration_days": 1
            }
        },
        {
            "name": "VIP Bronze - 15 Dias",
            "description": "Acesso VIP Bronze por 15 dias. Ideal para testar nossos benefícios exclusivos.",
            "price": 25.00,
            "category": "VIP",
            "vip_config": {
                "role_name": "VIP Bronze",
                "duration_days": 15
            }
        },
        {
            "name": "VIP Bronze - 30 Dias",
            "description": "Acesso VIP Bronze por 30 dias. Melhor custo-benefício para começar!",
            "price": 45.00,
            "category": "VIP",
            "vip_config": {
                "role_name": "VIP Bronze",
                "duration_days": 30
            }
        },
        {
            "name": "VIP Prata - 30 Dias",
            "description": "Acesso VIP Prata por 30 dias. Mais benefícios e vantagens exclusivas!",
            "price": 75.00,
            "category": "VIP",
            "vip_config": {
                "role_name": "VIP Prata",
                "duration_days": 30
            }
        },
        {
            "name": "VIP Ouro - 30 Dias",
            "description": "Acesso VIP Ouro por 30 dias. O melhor plano mensal com todos os benefícios!",
            "price": 120.00,
            "category": "VIP",
            "vip_config": {
                "role_name": "VIP Ouro",
                "duration_days": 30
            }
        },
        {
            "name": "VIP Diamante - Vitalício",
            "description": "Acesso VIP Diamante VITALÍCIO! Benefícios exclusivos para sempre. Investimento único!",
            "price": 500.00,
            "category": "VIP",
            "vip_config": {
                "role_name": "VIP Diamante",
                "duration_days": None  # Vitalício
            }
        }
    ]
    
    print("📦 Carregando novos produtos digitais...")
    for product in sample_products:
        await product_model.create_product(product)
    
    print(f"✅ {len(sample_products)} produtos digitais carregados com sucesso!")


@bot.command(name='products')
async def show_products(ctx):
    """Exibe os produtos disponíveis"""
    try:
        products = await product_model.get_all_products()
        
        if not products:
            await ctx.send("❌ Nenhum produto disponível no momento.")
            return
        
        embed = disnake.Embed(
            title="🛍️ Produtos Disponíveis",
            description="Escolha um produto para comprar:",
            color=0x8B5CF6
        )
        
        for product in products:
            embed.add_field(
                name=f"🛒 {product['name']}",
                value=f"**Preço:** R$ {product['price']:.2f}\n**Descrição:** {product['description']}",
                inline=False
            )
        
        embed.set_footer(text="Use ?buy <nome_do_produto> para comprar")
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
            await ctx.send("❌ Produto não encontrado. Use `?products` para ver os produtos disponíveis.")
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
            embed = disnake.Embed(
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
                # Usar QR Code base64 do Mercado Pago
                qr_image = payment_utils.get_qr_code_image_from_base64(payment_data['qr_code_base64'])
                if qr_image:
                    await ctx.send(file=disnake.File(qr_image, filename='qrcode.png'))
            elif payment_data.get('qr_code_image'):
                # Fallback para QR Code gerado localmente
                await ctx.send(file=disnake.File(payment_data['qr_code_image']))
            
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
                
                # Buscar dados da transação para logs
                transaction = await transaction_model.get_transaction(transaction_id)
                product_id = transaction.get('product_id') if transaction else None
                guild_id = transaction.get('guild_id') if transaction else None
                amount = transaction.get('amount', 0) if transaction else 0
                
                # Buscar dados do produto
                product_name = "Produto"
                if product_id and guild_id:
                    product_model = ProductModel()
                    product = await product_model.get_product_by_id(product_id, guild_id)
                    if product:
                        product_name = product.get('name', 'Produto')
                
                # LOG: Pagamento confirmado
                if hasattr(bot, 'log_system') and guild_id:
                    try:
                        user = bot.get_user(user_id)
                        if user:
                            await bot.log_system.log_payment_confirmed(
                                guild_id=guild_id,
                                user=user,
                                product_name=product_name,
                                amount=amount,
                                transaction_id=transaction_id
                            )
                    except Exception as log_err:
                        print(f"Erro ao enviar log de pagamento confirmado: {log_err}")
                
                # Enviar mensagem "Quase lá!"
                if user_id in active_tickets:
                    channel_id = active_tickets[user_id]['channel_id']
                    channel = bot.get_channel(channel_id)
                    
                    if channel:
                        # Mensagem de confirmação de pagamento
                        await channel.send(
                            "🎉 **Pagamento Confirmado!**\n"
                            "⏳ Processando entrega do produto...\n"
                            "📦 Aguarde apenas alguns segundos!"
                        )
                        
                        # Aguardar 3 segundos para criar expectativa
                        await asyncio.sleep(3)
                        
                        # Entrega do produto
                        embed = disnake.Embed(
                            title="✅ Produto Entregue!",
                            description="🎊 Sua compra foi concluída com sucesso! 🎊",
                            color=0x00ff00
                        )
                        
                        embed.add_field(
                            name="📦 Entrega Completa",
                            value="Seu produto foi entregue digitalmente neste canal.\n"
                                  "Verifique as mensagens acima para acessar seu produto!",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="💚 Obrigado pela Compra!",
                            value="Esperamos que aproveite seu produto.\n"
                                  "Qualquer dúvida, entre em contato com o suporte!",
                            inline=False
                        )
                        
                        embed.set_footer(text="Use /status para verificar o histórico • Ticket será fechado em breve")
                        
                        await channel.send(embed=embed)
                        
                        # LOG: Produto entregue
                        if hasattr(bot, 'log_system') and guild_id:
                            try:
                                user = bot.get_user(user_id)
                                if user:
                                    await bot.log_system.log_product_delivered(
                                        guild_id=guild_id,
                                        user=user,
                                        product_name=product_name,
                                        amount=amount,
                                        channel=channel
                                    )
                            except Exception as log_err:
                                print(f"Erro ao enviar log de produto entregue: {log_err}")
                        
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
                        await channel.send("❌ Pagamento não foi confirmado. Tente novamente com `?buy <produto>`")
                        
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
                    await channel.send("⏰ Tempo limite para pagamento expirado. Use `?buy <produto>` para tentar novamente.")
                    
                    # Limpar ticket ativo
                    del active_tickets[user_id]
                    
    except Exception as e:
        print(f"Erro ao monitorar pagamento: {e}")


# Comando de teste via prefixo
@bot.command(name='teste')
async def teste_prefix(ctx):
    """Comando de teste via prefixo"""
    print(f"🔧 Comando ?teste executado por {ctx.author.name} em {ctx.guild.name}")
    await ctx.send("✅ Comando ?teste funcionando via prefixo!")

# Comando para forçar sincronização de slash commands
@bot.command(name='sync')
@commands.has_permissions(administrator=True)
async def sync_commands(ctx):
    """Força a sincronização dos comandos slash"""
    try:
        print(f"🔄 Comando de sincronização executado por {ctx.author.name}")
        
        # Listar comandos registrados
        commands = getattr(bot, 'pending_application_commands', list(bot.application_commands))
        await ctx.send(f"📋 Comandos registrados: {len(commands)}")
        for cmd in commands:
            await ctx.send(f"  - /{cmd.name}: {cmd.description}")
        
        # Tentar sincronizar globalmente
        try:
            # Em disnake, use sync_all_commands
            if hasattr(bot, 'sync_all_commands'):
                await bot.sync_all_commands()
                await ctx.send("✅ Comandos sincronizados usando sync_all_commands!")
            else:
                await ctx.send("⚠️ sync_all_commands não disponível, usando sincronização automática")
        except Exception as e:
            await ctx.send(f"❌ Erro na sincronização global: {e}")
            
            # Tentar sincronizar por guild
            try:
                if hasattr(bot, 'sync_commands_force'):
                    await bot.sync_commands_force([ctx.guild.id])
                    await ctx.send("✅ Comandos sincronizados na guild usando sync_commands_force!")
                else:
                    await ctx.send("⚠️ sync_commands_force não disponível")
            except Exception as guild_error:
                await ctx.send(f"❌ Erro na sincronização da guild: {guild_error}")
            
    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

# Comando para recarregar produtos
@bot.command(name='reload_products')
@commands.has_permissions(administrator=True)
async def reload_products(ctx):
    """Recarrega os produtos no banco de dados"""
    await ctx.send("⚠️ **Comando Obsoleto!**\n\n"
                  "Este comando não funciona mais com o sistema multi-servidor.\n\n"
                  "**Use os novos comandos:**\n"
                  "`/admin_criar_produto` - Criar produto\n"
                  "`/admin_criar_vip` - Criar VIP\n"
                  "`/admin_listar_produtos` - Ver produtos\n"
                  "`/admin_deletar_produto` - Deletar produtos")

# Comando para adicionar estoque via prefixo
@bot.command(name='adicionar_estoque', aliases=['add_stock'])
@commands.has_permissions(administrator=True)
async def add_stock_prefix(ctx):
    """Adicionar itens ao estoque de um produto (versão prefixo)"""
    try:
        # Buscar todos os produtos
        from models.product_model import ProductModel
        product_model = ProductModel()
        products = await product_model.get_all_products()
        
        if not products:
            await ctx.send("❌ Nenhum produto cadastrado.")
            return
        
        # Criar embed com lista de produtos
        embed = disnake.Embed(
            title="➕ Adicionar Estoque",
            description="**Produtos disponíveis:**",
            color=0x8B5CF6
        )
        
        for i, p in enumerate(products[:10], 1):  # Limitar a 10 produtos
            embed.add_field(
                name=f"{i}. {p['name']}",
                value=f"R$ {p['price']:.2f} • ID: {p['id']}",
                inline=False
            )
        
        embed.add_field(
            name="📝 Como adicionar estoque:",
            value="Use o comando slash `/adicionar_estoque` para uma interface melhor!\n\n"
                  "Ou envie neste chat:\n"
                  f"`?add_stock_id <ID> <códigos>`\n\n"
                  "Exemplo:\n"
                  f"`?add_stock_id {products[0]['id']}`\n"
                  "Depois cole os códigos, um por linha.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando ?adicionar_estoque: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Erro: {str(e)}")

# Comando auxiliar para adicionar estoque por ID
@bot.command(name='add_stock_id')
@commands.has_permissions(administrator=True)
async def add_stock_by_id(ctx, product_id: int):
    """Adiciona estoque para um produto específico"""
    try:
        from models.product_model import ProductModel
        from models.inventory_model import InventoryModel
        
        product_model = ProductModel()
        product = await product_model.get_product_by_id(product_id)
        
        if not product:
            await ctx.send(f"❌ Produto com ID {product_id} não encontrado.")
            return
        
        await ctx.send(f"📦 **{product['name']}**\n\n"
                      f"Cole os códigos/keys abaixo (um por linha).\n"
                      f"Quando terminar, envie `?done` ou aguarde 30 segundos.")
        
        # Esperar pelas mensagens do usuário
        codes = []
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        for _ in range(100):  # Máximo 100 códigos por vez
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=check)
                
                if msg.content.lower() in ['?done', 'done', 'pronto', '?pronto']:
                    break
                
                # Adicionar códigos
                lines = msg.content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('?'):
                        codes.append(line)
                
                if len(codes) > 0:
                    await msg.add_reaction('✅')
                    
            except TimeoutError:
                break
        
        if not codes:
            await ctx.send("❌ Nenhum código fornecido.")
            return
        
        # Adicionar ao estoque
        inventory_model = InventoryModel()
        added = await inventory_model.add_bulk_stock(product_id, codes)
        
        if added > 0:
            embed = disnake.Embed(
                title="✅ Estoque Adicionado",
                description=f"**{added}** itens foram adicionados ao produto **{product['name']}**.",
                color=0x00ff00
            )
            embed.add_field(name="📦 Produto", value=product['name'], inline=True)
            embed.add_field(name="➕ Itens Adicionados", value=str(added), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Erro ao adicionar estoque.")
            
    except Exception as e:
        print(f"Erro ao adicionar estoque por ID: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Erro: {str(e)}")

# Comando para ver estoque via prefixo
@bot.command(name='ver_estoque', aliases=['stock', 'estoque'])
@commands.has_permissions(administrator=True)
async def view_stock_prefix(ctx):
    """Ver resumo do estoque de produtos (versão prefixo)"""
    try:
        from models.inventory_model import InventoryModel
        
        inventory_model = InventoryModel()
        summary = await inventory_model.get_all_stock_summary()
        
        if not summary:
            await ctx.send("❌ Nenhum produto com estoque.")
            return
        
        # Criar embed com resumo
        embed = disnake.Embed(
            title="📊 Resumo de Estoque",
            description="Status de estoque de todos os produtos",
            color=0x8B5CF6
        )
        
        for item in summary:
            status_emoji = "✅" if item['available'] > 0 else "❌"
            value = f"{status_emoji} Disponível: **{item['available']}**\n"
            value += f"🔒 Reservado: {item['reserved']}\n"
            value += f"💰 Vendido: {item['sold']}\n"
            value += f"📦 Total: {item['total']}"
            
            embed.add_field(
                name=f"{item['product_name']}",
                value=value,
                inline=True
            )
        
        embed.set_footer(text="Use /adicionar_estoque para adicionar mais itens")
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando !ver_estoque: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Erro: {str(e)}")

# Comando para configurar ticket com imagem e personalização
@bot.command(name='setup_ticket_img')
@commands.has_permissions(administrator=True)
async def setup_ticket_with_image(ctx, *, args=""):
    """Configura sistema de tickets com imagem e personalização
    
    Uso: !setup_ticket_img [título] [cor] [nome_botão]
    Ex: !setup_ticket_img "🛒 Vendas Premium" "#ff0000" "Comprar Agora"
    """
    try:
        # Verificar se há anexos
        if not ctx.message.attachments:
            await ctx.send("❌ **Como usar:**\n"
                          "1. Arraste uma imagem para o chat\n"
                          "2. Use: `!setup_ticket_img [título] [cor] [nome_botão]`\n"
                          "3. Ex: `!setup_ticket_img \"🛒 Vendas Premium\" \"#ff0000\" \"Comprar Agora\"`")
            return
        
        # Pegar a primeira imagem
        attachment = ctx.message.attachments[0]
        
        # Verificar se é uma imagem
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            await ctx.send("❌ O arquivo deve ser uma imagem!")
            return
        
        # Processar argumentos
        parts = args.split('"') if '"' in args else args.split()
        titulo = parts[1] if len(parts) > 1 and parts[1].strip() else "🛒 Sistema de Vendas Automatizado"
        cor = parts[3] if len(parts) > 3 and parts[3].strip() else "#0099ff"
        nome_botao = parts[5] if len(parts) > 5 and parts[5].strip() else "Criar Ticket de Compra"
        
        # Converter cor hex para int
        try:
            cor_hex = cor.strip().lower()
            if cor_hex.startswith('#'):
                cor_hex = cor_hex[1:]
            elif cor_hex.startswith('0x'):
                cor_hex = cor_hex[2:]
            
            if len(cor_hex) == 3:
                cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
            
            cor_int = int(cor_hex, 16)
            print(f"Cor convertida: {cor_int} (0x{cor_hex})")
        except (ValueError, IndexError):
            print(f"Cor inválida '{cor}', usando padrão")
            cor_int = 0x0099ff
        
        # Criar embed personalizado
        embed = disnake.Embed(
            title=titulo,
            description="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            color=cor_int
        )
        embed.set_image(url=attachment.url)
        embed.add_field(
            name="🚀 Como Funciona?",
            value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
            inline=False
        )
        embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")
        
        # Criar view com botão personalizado
        from utils.ticket_views import TicketView
        view = TicketView(nome_botao)
        
        await ctx.send(embed=embed, view=view)
        await ctx.send(f"✅ Sistema de tickets configurado!\n"
                      f"**Título:** {titulo}\n"
                      f"**Cor:** {cor} (0x{cor_hex})\n"
                      f"**Botão:** {nome_botao}")
        
    except Exception as e:
        print(f"Erro no setup_ticket_img: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send("❌ Erro ao configurar sistema de tickets.")

# ========================================
# COMANDOS ADMIN MULTI-SERVIDOR
# ========================================

@bot.slash_command(name="admin_criar_produto", description="[ADMIN] Criar um produto no servidor")
@commands.has_permissions(administrator=True)
async def admin_criar_produto(
    ctx: disnake.ApplicationCommandInteraction,
    nome: str,
    preco: float,
    descricao: str,
    categoria: str = "produto",
    estoque_ilimitado: bool = False
):
    """Criar produto que atualiza diretamente no Supabase"""
    try:
        await ctx.response.defer(ephemeral=True)
        
        product_data = {
            'name': nome,
            'price': preco,
            'description': descricao,
            'category': categoria,
            'unlimited_stock': estoque_ilimitado
        }
        
        product = await product_model.create_product(ctx.guild_id, product_data)
        
        if product:
            embed = disnake.Embed(
                title="✅ Produto Criado no Supabase",
                description=f"Produto **{nome}** criado com sucesso!",
                color=disnake.Color.green()
            )
            embed.add_field(name="ID", value=product['id'], inline=True)
            embed.add_field(name="Preço", value=f"R$ {preco:.2f}", inline=True)
            embed.add_field(name="Categoria", value=categoria, inline=True)
            embed.add_field(name="Estoque", value="♾️ Ilimitado" if estoque_ilimitado else "📦 Gerenciado", inline=True)
            
            await ctx.followup.send(embed=embed, ephemeral=True)
        else:
            await ctx.followup.send("❌ Erro ao criar produto no Supabase.", ephemeral=True)
            
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        await ctx.followup.send(f"❌ Erro: {e}", ephemeral=True)


@bot.slash_command(name="admin_deletar_produto", description="[ADMIN] Deletar um ou mais produtos do servidor")
@commands.has_permissions(administrator=True)
async def admin_deletar_produto(inter: disnake.ApplicationCommandInteraction, product_ids: str):
    """Deletar um ou mais produtos do Supabase"""
    try:
        await inter.response.defer(ephemeral=True)
        
        # Parse dos IDs (aceita vírgula ou espaço)
        ids_str = product_ids.replace(',', ' ').split()
        
        try:
            ids = [int(id_str.strip()) for id_str in ids_str if id_str.strip().isdigit()]
        except ValueError:
            await inter.followup.send("❌ IDs inválidos. Use números separados por vírgula (ex: 1,2,3)", ephemeral=True)
            return
        
        if not ids:
            await inter.followup.send("❌ Nenhum ID válido fornecido.", ephemeral=True)
            return
        
        # Deletar cada produto
        deleted = []
        not_found = []
        errors = []
        
        for product_id in ids:
            # Buscar produto para confirmar
            product = await product_model.get_product_by_id(product_id, inter.guild_id)
            
            if not product:
                not_found.append(product_id)
                continue
            
            # Deletar do Supabase
            success = await product_model.delete_product(product_id, inter.guild_id)
            
            if success:
                deleted.append(f"**{product['name']}** (ID: {product_id})")
            else:
                errors.append(product_id)
        
        # Criar embed de resultado
        embed = disnake.Embed(
            title="🗑️ Resultado da Exclusão",
            color=disnake.Color.green() if deleted else disnake.Color.red()
        )
        
        if deleted:
            embed.add_field(
                name=f"✅ Deletados ({len(deleted)})",
                value="\n".join(deleted),
                inline=False
            )
        
        if not_found:
            embed.add_field(
                name=f"❌ Não Encontrados ({len(not_found)})",
                value=", ".join(map(str, not_found)),
                inline=False
            )
        
        if errors:
            embed.add_field(
                name=f"⚠️ Erros ao Deletar ({len(errors)})",
                value=", ".join(map(str, errors)),
                inline=False
            )
        
        await inter.followup.send(embed=embed, ephemeral=True)
            
    except Exception as e:
        print(f"Erro ao deletar produtos: {e}")
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)


@bot.slash_command(name="admin_listar_produtos", description="[ADMIN] Listar todos os produtos do servidor")
@commands.has_permissions(administrator=True)
async def admin_listar_produtos(inter: disnake.ApplicationCommandInteraction):
    """Listar produtos do Supabase"""
    try:
        await inter.response.defer(ephemeral=True)
        
        products = await product_model.get_products_by_guild(inter.guild_id)
        
        if not products:
            await inter.followup.send("📦 Nenhum produto cadastrado neste servidor no Supabase.", ephemeral=True)
            return
        
        # Separar por categoria
        vips = [p for p in products if p.get('category') == 'vip']
        normais = [p for p in products if p.get('category') != 'vip']
        
        embed = disnake.Embed(
            title=f"📦 Produtos do Servidor ({len(products)} total)",
            description="Produtos cadastrados no Supabase",
            color=disnake.Color.blue()
        )
        
        if normais:
            produtos_text = "\n".join([
                f"**ID {p['id']}** - {p['name']} - R$ {p['price']:.2f} {'♾️' if p.get('unlimited_stock') else '📦'}"
                for p in normais[:10]
            ])
            embed.add_field(
                name=f"🛍️ Produtos Normais ({len(normais)})",
                value=produtos_text or "Nenhum",
                inline=False
            )
        
        if vips:
            vips_text = "\n".join([
                f"**ID {p['id']}** - {p['name']} - R$ {p['price']:.2f} {'♾️' if p.get('unlimited_stock') else '📦'}"
                for p in vips[:10]
            ])
            embed.add_field(
                name=f"👑 Produtos VIP ({len(vips)})",
                value=vips_text or "Nenhum",
                inline=False
            )
        
        if len(products) > 20:
            embed.set_footer(text=f"Mostrando 20 de {len(products)} produtos")
        
        await inter.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)


@bot.slash_command(name="admin_criar_vip", description="[ADMIN] Criar produto VIP no servidor")
@commands.has_permissions(administrator=True)
async def admin_criar_vip(
    ctx: disnake.ApplicationCommandInteraction,
    nome: str,
    preco: float,
    role_name: str,
    descricao: str,
    duracao_dias: int = 0
):
    """Criar produto VIP no Supabase"""
    try:
        await ctx.response.defer(ephemeral=True)
        
        # Configuração VIP
        vip_config = {
            "role_name": role_name,
            "duration_days": duracao_dias if duracao_dias > 0 else None
        }
        
        product_data = {
            'name': nome,
            'price': preco,
            'description': descricao,
            'category': 'vip',
            'vip_config': vip_config,
            'unlimited_stock': True  # VIPs sempre têm estoque ilimitado
        }
        
        product = await product_model.create_product(ctx.guild_id, product_data)
        
        if product:
            duracao_text = f"{duracao_dias} dias" if duracao_dias > 0 else "Vitalício"
            
            embed = disnake.Embed(
                title="✅ Produto VIP Criado no Supabase",
                description=f"VIP **{nome}** criado com sucesso!",
                color=disnake.Color.gold()
            )
            embed.add_field(name="ID", value=product['id'], inline=True)
            embed.add_field(name="Preço", value=f"R$ {preco:.2f}", inline=True)
            embed.add_field(name="Role", value=role_name, inline=True)
            embed.add_field(name="Duração", value=duracao_text, inline=True)
            
            await ctx.followup.send(embed=embed, ephemeral=True)
        else:
            await ctx.followup.send("❌ Erro ao criar produto VIP.", ephemeral=True)
            
    except Exception as e:
        print(f"Erro ao criar VIP: {e}")
        await ctx.followup.send(f"❌ Erro: {e}", ephemeral=True)


# =============================================
# COMANDOS MICRO SAAS - CARTEIRA VIRTUAL
# =============================================

@bot.slash_command(name="saldo", description="Ver saldo disponível e estatísticas da carteira")
@commands.has_permissions(administrator=True)
async def saldo_cmd(inter: disnake.ApplicationCommandInteraction):
    """Ver saldo e estatísticas da carteira do servidor"""
    try:
        await inter.response.defer(ephemeral=True)
        
        from models.wallet_model import WalletModel
        wallet_model = WalletModel()
        
        # Buscar estatísticas
        stats = await wallet_model.get_wallet_stats(inter.guild_id)
        
        # Criar embed
        embed = disnake.Embed(
            title="💰 Carteira do Servidor",
            description=f"Estatísticas financeiras de **{inter.guild.name}**",
            color=disnake.Color.green()
        )
        
        # Saldo disponível
        embed.add_field(
            name="💵 Saldo Disponível",
            value=f"R$ {stats['balance_available']:.2f}",
            inline=True
        )
        
        # Saldo pendente
        embed.add_field(
            name="⏳ Saldo Pendente",
            value=f"R$ {stats['balance_pending']:.2f}",
            inline=True
        )
        
        # Total ganho
        embed.add_field(
            name="📈 Total Ganho",
            value=f"R$ {stats['total_earned']:.2f}",
            inline=True
        )
        
        # Total sacado
        embed.add_field(
            name="💸 Total Sacado",
            value=f"R$ {stats['total_withdrawn']:.2f}",
            inline=True
        )
        
        # Taxas pagas
        embed.add_field(
            name="💳 Taxas Pagas",
            value=f"R$ {stats['platform_fees_paid']:.2f}",
            inline=True
        )
        
        # Lucro líquido
        embed.add_field(
            name="💎 Lucro Líquido",
            value=f"R$ {stats['net_profit']:.2f}",
            inline=True
        )
        
        # Chave Pix configurada
        if stats.get('pix_key'):
            embed.add_field(
                name="🔑 Chave Pix Cadastrada",
                value=f"Tipo: {stats['pix_type'].upper()}",
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Chave Pix",
                value="Use `/configurar_pix` para cadastrar",
                inline=False
            )
        
        embed.set_footer(text=f"Use /solicitar_saque para sacar • Mínimo: R$ 10,00")
        
        await inter.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao buscar saldo: {e}")
        import traceback
        traceback.print_exc()
        await inter.followup.send(f"❌ Erro ao buscar saldo: {e}", ephemeral=True)


@bot.slash_command(name="configurar_pix", description="Cadastrar chave Pix padrão para saques")
@commands.has_permissions(administrator=True)
async def configurar_pix_cmd(inter: disnake.ApplicationCommandInteraction, chave_pix: str, tipo: str):
    """Cadastrar chave Pix padrão"""
    try:
        await inter.response.defer(ephemeral=True)
        
        from models.wallet_model import WalletModel
        from utils.withdrawal_manager import WithdrawalManager
        
        wallet_model = WalletModel()
        withdrawal_manager = WithdrawalManager()
        
        # Validar chave Pix
        valid, result = withdrawal_manager.validate_pix_key(chave_pix, tipo)
        
        if not valid:
            await inter.followup.send(result, ephemeral=True)
            return
        
        # Salvar
        success = await wallet_model.save_pix_key(inter.guild_id, result, tipo)
        
        if success:
            # Mascarar chave para exibir
            if tipo == 'cpf':
                masked = f"{result[:3]}.XXX.XXX-{result[-2:]}"
            elif tipo == 'email':
                parts = result.split('@')
                masked = f"{parts[0][:2]}***@{parts[1]}"
            elif tipo == 'phone':
                masked = f"{result[:3]}***{result[-4:]}"
            else:
                masked = f"{result[:5]}***{result[-4:]}"
            
            embed = disnake.Embed(
                title="✅ Chave Pix Cadastrada",
                description=f"Chave Pix salva com sucesso!",
                color=disnake.Color.green()
            )
            embed.add_field(name="Tipo", value=tipo.upper(), inline=True)
            embed.add_field(name="Chave", value=masked, inline=True)
            embed.set_footer(text="Esta chave será usada como padrão nos saques")
            
            await inter.followup.send(embed=embed, ephemeral=True)
        else:
            await inter.followup.send("❌ Erro ao salvar chave Pix", ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao configurar Pix: {e}")
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)


@bot.slash_command(name="solicitar_saque", description="Solicitar saque via Pix")
@commands.has_permissions(administrator=True)
async def solicitar_saque_cmd(inter: disnake.ApplicationCommandInteraction):
    """Solicitar saque via modal"""
    try:
        # Criar modal para saque
        class WithdrawalModal(disnake.ui.Modal, title="💸 Solicitar Saque"):
            def __init__(self):
                components = [
                    disnake.ui.TextInput(
                label="Valor a Sacar (R$)",
                placeholder="Ex: 50.00",
                        custom_id="amount",
                required=True,
                min_length=1,
                max_length=10
                    ),
                    disnake.ui.TextInput(
                label="Chave Pix",
                placeholder="CPF, email, telefone, etc (ou deixe vazio para usar padrão)",
                        custom_id="pix_key",
                required=False,
                max_length=255
                    ),
                    disnake.ui.TextInput(
                label="Tipo da Chave Pix",
                placeholder="cpf, cnpj, email, phone ou random",
                        custom_id="pix_type",
                required=False,
                max_length=10
            )
                ]
                super().__init__(title="💸 Solicitar Saque", components=components)
            
            async def callback(self, interaction: disnake.ModalInteraction):
                await interaction.response.defer(ephemeral=True)
                
                try:
                    from decimal import Decimal
                    from models.wallet_model import WalletModel
                    from utils.withdrawal_manager import WithdrawalManager
                    
                    wallet_model = WalletModel()
                    withdrawal_manager = WithdrawalManager()
                    
                    # Validar valor
                    try:
                        amount = Decimal(interaction.text_values.get("amount", "0").replace(',', '.'))
                    except:
                        await interaction.followup.send("❌ Valor inválido. Use formato: 50.00", ephemeral=True)
                        return
                    
                    # Buscar chave Pix (usar padrão se não informada)
                    pix_key = interaction.text_values.get("pix_key", "").strip()
                    pix_type = interaction.text_values.get("pix_type", "").strip().lower()
                    
                    if not pix_key:
                        # Usar chave padrão
                        wallet = await wallet_model.get_wallet(interaction.guild_id)
                        if not wallet or not wallet.get('pix_key'):
                            await interaction.followup.send(
                                "❌ Nenhuma chave Pix cadastrada. Use `/configurar_pix` primeiro ou informe a chave no formulário.",
                                ephemeral=True
                            )
                            return
                        
                        pix_key = wallet['pix_key']
                        pix_type = wallet['pix_type']
                    
                    # Validar tipo
                    if pix_type not in ['cpf', 'cnpj', 'email', 'phone', 'random']:
                        await interaction.followup.send("❌ Tipo de chave inválido. Use: cpf, cnpj, email, phone ou random", ephemeral=True)
                        return
                    
                    # Criar solicitação
                    withdrawal = await withdrawal_manager.create_withdrawal_request(
                        guild_id=interaction.guild_id,
                        user_id=interaction.user.id,
                        amount=amount,
                        pix_key=pix_key,
                        pix_type=pix_type
                    )
                    
                    if not withdrawal:
                        await interaction.followup.send("❌ Erro ao criar solicitação de saque. Verifique seu saldo.", ephemeral=True)
                        return
                    
                    # Calcular taxas
                    fees = await wallet_model.calculate_withdrawal_fees(amount)
                    
                    # Enviar confirmação
                    embed = disnake.Embed(
                        title="📝 Solicitação de Saque Criada",
                        description="Seu saque será processado automaticamente!",
                        color=disnake.Color.blue()
                    )
                    embed.add_field(name="Valor Solicitado", value=f"R$ {amount:.2f}", inline=True)
                    embed.add_field(name="Taxa (3%)", value=f"R$ {fees['fee_amount']:.2f}", inline=True)
                    embed.add_field(name="Você Receberá", value=f"R$ {fees['net_amount']:.2f}", inline=True)
                    embed.add_field(name="Chave Pix", value=f"{pix_type.upper()}", inline=True)
                    embed.add_field(name="Status", value="⏳ Processando...", inline=True)
                    embed.set_footer(text=f"ID: #{withdrawal['id']}")
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    
                    # Processar saque imediatamente em background
                    import asyncio
                    asyncio.create_task(withdrawal_manager.process_withdrawal(withdrawal['id']))
                    
                except Exception as e:
                    print(f"Erro ao processar saque: {e}")
                    import traceback
                    traceback.print_exc()
                    await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)
        
        # Mostrar modal
        await inter.response.send_modal(WithdrawalModal())
        
    except Exception as e:
        print(f"Erro ao abrir modal de saque: {e}")
        await inter.response.send_message(f"❌ Erro: {e}", ephemeral=True)


@bot.slash_command(name="historico_vendas", description="Ver histórico de vendas e movimentações")
@commands.has_permissions(administrator=True)
async def historico_vendas_cmd(inter: disnake.ApplicationCommandInteraction):
    """Ver histórico de transações da carteira"""
    try:
        await inter.response.defer(ephemeral=True)
        
        from models.wallet_model import WalletModel
        wallet_model = WalletModel()
        
        # Buscar histórico
        history = await wallet_model.get_wallet_history(inter.guild_id, limit=10)
        
        if not history:
            await inter.followup.send("📭 Nenhuma movimentação encontrada.", ephemeral=True)
            return
        
        # Criar embed
        embed = disnake.Embed(
            title="📊 Histórico de Movimentações",
            description=f"Últimas 10 transações da carteira",
            color=disnake.Color.blue()
        )
        
        for tx in history[:10]:
            tx_type = tx['type']
            
            # Ícone baseado no tipo
            if 'credit' in tx_type:
                icon = "💰"
                type_name = "Venda"
            elif 'debit' in tx_type:
                icon = "💸"
                type_name = "Saque"
            elif 'fee' in tx_type:
                icon = "💳"
                type_name = "Taxa"
            else:
                icon = "📌"
                type_name = "Outro"
            
            value_str = f"R$ {tx['net_amount']:.2f}"
            if tx.get('platform_fee', 0) > 0:
                value_str += f" (taxa: R$ {tx['platform_fee']:.2f})"
            
            embed.add_field(
                name=f"{icon} {type_name} - {tx['created_at'][:10]}",
                value=f"{value_str}\nSaldo após: R$ {tx['balance_after']:.2f}",
                inline=False
            )
        
        await inter.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)


@bot.slash_command(name="historico_saques", description="Ver histórico de saques processados")
@commands.has_permissions(administrator=True)
async def historico_saques_cmd(inter: disnake.ApplicationCommandInteraction):
    """Ver histórico de saques"""
    try:
        await inter.response.defer(ephemeral=True)
        
        from utils.withdrawal_manager import WithdrawalManager
        withdrawal_manager = WithdrawalManager()
        
        # Buscar histórico
        history = await withdrawal_manager.get_withdrawal_history(inter.guild_id, limit=10)
        
        if not history:
            await inter.followup.send("📭 Nenhum saque encontrado.", ephemeral=True)
            return
        
        # Criar embed
        embed = disnake.Embed(
            title="💸 Histórico de Saques",
            description=f"Últimos 10 saques solicitados",
            color=disnake.Color.purple()
        )
        
        for withdrawal in history:
            status = withdrawal['status']
            
            # Ícone baseado no status
            status_icons = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'failed': '❌',
                'rejected': '🚫',
                'cancelled': '⛔'
            }
            icon = status_icons.get(status, '❓')
            
            value_text = f"Solicitado: R$ {withdrawal['amount_requested']:.2f}\n"
            value_text += f"Taxa: R$ {withdrawal['fee_amount']:.2f}\n"
            value_text += f"Recebido: R$ {withdrawal['net_amount']:.2f}"
            
            embed.add_field(
                name=f"{icon} Saque #{withdrawal['id']} - {status.upper()}",
                value=value_text,
                inline=False
            )
        
        await inter.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao buscar saques: {e}")
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)

@bot.slash_command(name="verificar_pagamentos", description="[ADMIN] Verificar pagamentos pendentes manualmente")
@commands.has_permissions(administrator=True)
async def verificar_pagamentos_cmd(inter: disnake.ApplicationCommandInteraction):
    """Verificar pagamentos pendentes manualmente (enquanto webhook não está configurado)"""
    try:
        await inter.response.defer(ephemeral=True)
        
        from models.transaction_model import TransactionModel
        from utils.mercadopago_manager import MercadoPagoManager
        from models.wallet_model import WalletModel
        from utils.delivery_manager import DeliveryManager
        
        transaction_model = TransactionModel()
        mp_manager = MercadoPagoManager()
        wallet_model = WalletModel()
        delivery_manager = DeliveryManager(bot)
        
        # Buscar transações pendentes deste servidor
        print(f"🔍 Verificando pagamentos pendentes do servidor {inter.guild_id}")
        
        # Query manual para buscar transações pendentes
        result = transaction_model.supabase.table('transactions')\
            .select('*')\
            .eq('guild_id', inter.guild_id)\
            .eq('status', 'pending')\
            .order('created_at', desc=True)\
            .limit(10)\
            .execute()
        
        pending_transactions = result.data if result.data else []
        
        if not pending_transactions:
            await inter.followup.send("✅ Nenhum pagamento pendente encontrado!", ephemeral=True)
            return
        
        # Verificar cada transação
        checked = 0
        approved = 0
        
        for transaction in pending_transactions:
            payment_id = transaction.get('payment_id')
            if not payment_id:
                continue
            
            checked += 1
            print(f"🔍 Verificando pagamento {payment_id}...")
            
            # Consultar status no Mercado Pago
            payment_info = await mp_manager.check_payment_status(payment_id)
            
            if payment_info and payment_info.get('status') == 'approved':
                print(f"✅ Pagamento {payment_id} APROVADO!")
                approved += 1
                
                # Atualizar transação
                await transaction_model.update_transaction(transaction['id'], {
                    'status': 'approved',
                    'gateway_used': 'mercadopago'
                })
                
                # Creditar carteira (descontando R$ 0,80)
                amount = float(transaction['amount'])
                platform_fee = 0.80
                net_amount = amount - platform_fee
                
                await wallet_model.credit_wallet(
                    guild_id=inter.guild_id,
                    amount=net_amount,
                    transaction_id=transaction['id'],
                    platform_fee=platform_fee,
                    description=f"Venda aprovada - Transaction #{transaction['id']}"
                )
                
                print(f"💰 Carteira creditada: R$ {net_amount:.2f} (R$ {amount:.2f} - R$ {platform_fee:.2f})")
                
                # Entregar produto
                try:
                    await delivery_manager.deliver_product(transaction['id'])
                    print(f"📦 Produto entregue!")
                except Exception as delivery_error:
                    print(f"⚠️ Erro ao entregar produto: {delivery_error}")
        
        # Resposta
        embed = disnake.Embed(
            title="🔍 Verificação de Pagamentos",
            color=disnake.Color.green() if approved > 0 else disnake.Color.blue()
        )
        
        embed.add_field(name="📊 Total verificado", value=str(checked), inline=True)
        embed.add_field(name="✅ Aprovados", value=str(approved), inline=True)
        embed.add_field(name="⏳ Pendentes", value=str(checked - approved), inline=True)
        
        if approved > 0:
            embed.add_field(
                name="💰 Ação tomada",
                value=f"✅ {approved} pagamento(s) processado(s)\n"
                      f"💵 Carteira creditada\n"
                      f"📦 Produto(s) entregue(s)",
                inline=False
            )
        
        embed.set_footer(text="Use /saldo para ver o saldo atualizado")
        
        await inter.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"❌ Erro ao verificar pagamentos: {e}")
        import traceback
        traceback.print_exc()
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)


# Sistema de espera para adicionar estoque
waiting_for_stock = {}

# Listener para capturar mensagens de estoque
@bot.event
async def on_message(message):
    # Ignorar mensagens do próprio bot
    if message.author.bot:
        return
    
    # Nota: Sistema de aguardar input foi removido - agora usando modais exclusivamente
    
    # Debug: Log de mensagens que começam com ?
    if message.content.startswith('?'):
        print(f"🔧 DEBUG: Mensagem com prefixo detectada: {message.content[:50]}...")
        print(f"🔧 DEBUG: Autor: {message.author.name}, Canal: {message.channel.name}")
    
    # Processar comandos com prefixo
    await bot.process_commands(message)
    
    # Verificar se está esperando códigos de estoque
    if message.author.id in waiting_for_stock:
        data = waiting_for_stock[message.author.id]
        
        # Verificar se é no canal correto
        if message.channel.id == data['channel_id']:
            try:
                # Processar os códigos
                codes = [line.strip() for line in message.content.split('\n') if line.strip()]
                
                if not codes:
                    await message.reply("❌ Nenhum código válido encontrado.")
                    return
                
                # Adicionar ao estoque
                from models.inventory_model import InventoryModel
                inventory_model = InventoryModel()
                
                added_count = 0
                for code in codes:
                    success = await inventory_model.add_stock(
                        product_id=data['product']['id'],
                        guild_id=data['guild_id'],
                        content=code
                    )
                    if success:
                        added_count += 1
                
                # Embed de sucesso
                embed = disnake.Embed(
                    title="✅ Estoque Adicionado",
                    description=f"Códigos adicionados ao produto **{data['product']['name']}**",
                    color=disnake.Color.green()
                )
                embed.add_field(name="📦 Produto", value=data['product']['name'], inline=True)
                embed.add_field(name="✅ Adicionados", value=f"{added_count} códigos", inline=True)
                embed.add_field(name="❌ Falharam", value=f"{len(codes) - added_count}", inline=True)
                
                if added_count < len(codes):
                    embed.add_field(
                        name="⚠️ Atenção",
                        value=f"{len(codes) - added_count} código(s) já existem ou falharam.",
                        inline=False
                    )
                
                await message.reply(embed=embed)
                
                # Remover da fila de espera
                del waiting_for_stock[message.author.id]
                
                # Deletar mensagem com os códigos por segurança
                try:
                    await message.delete()
                except:
                    pass
                
            except Exception as e:
                print(f"Erro ao processar códigos: {e}")
                await message.reply(f"❌ Erro ao adicionar estoque: {e}")
                del waiting_for_stock[message.author.id]


@bot.slash_command(name="adicionar_estoque", description="[ADMIN] Adicionar códigos/keys ao estoque")
@commands.has_permissions(administrator=True)
async def adicionar_estoque(inter: disnake.ApplicationCommandInteraction):
    """Adicionar códigos ao estoque de produtos"""
    try:
        await inter.response.defer(ephemeral=True)
        
        # Buscar produtos do servidor (exceto VIPs e ilimitados)
        products = await product_model.get_products_by_guild(inter.guild_id)
        
        # Filtrar apenas produtos que precisam de estoque
        products_with_stock = [
            p for p in products 
            if not p.get('unlimited_stock') and p.get('category') != 'vip'
        ]
        
        if not products_with_stock:
            embed = disnake.Embed(
                title="⚠️ Nenhum Produto com Estoque Gerenciado",
                description="Todos os produtos do servidor são ilimitados ou VIPs (não precisam de estoque).",
                color=disnake.Color.orange()
            )
            embed.add_field(
                name="💡 Dica",
                value="Use `/admin_criar_produto` com `estoque_ilimitado: False` para criar produtos que precisam de estoque.",
                inline=False
            )
            await inter.followup.send(embed=embed, ephemeral=True)
            return
        
        # Criar Select Menu com produtos
        class ProductSelect(disnake.ui.Select):
            def __init__(self, products):
                self.products = products
                options = [
                    disnake.SelectOption(
                        label=p['name'][:100],
                        description=f"R$ {p['price']:.2f} • ID: {p['id']}",
                        value=str(p['id'])
                    )
                    for p in products[:25]  # Discord limita a 25 opções
                ]
                super().__init__(placeholder="Escolha um produto...", options=options)
            
            async def callback(self, interaction: disnake.ModalInteraction):
                try:
                    product_id = int(self.values[0])
                    product = next((p for p in self.products if p['id'] == product_id), None)
                    
                    if product:
                        # Registrar que está esperando códigos deste usuário
                        waiting_for_stock[interaction.user.id] = {
                            'product': product,
                            'guild_id': interaction.guild_id,
                            'channel_id': interaction.channel_id
                        }
                        
                        embed = disnake.Embed(
                            title="📝 Envie os Códigos",
                            description=f"Produto selecionado: **{product['name']}**\n\n"
                                       f"Envie os códigos/keys neste canal, **um por linha**.\n"
                                       f"Exemplo:",
                            color=disnake.Color.blue()
                        )
                        embed.add_field(
                            name="Formato:",
                            value="```\nCODIGO1-XXXX-YYYY-ZZZZ\nCODIGO2-AAAA-BBBB-CCCC\nCODIGO3-EMAIL:SENHA\n```",
                            inline=False
                        )
                        embed.set_footer(text="Você tem 5 minutos para enviar os códigos")
                        
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Produto não encontrado.", ephemeral=True)
                except Exception as e:
                    print(f"Erro no select callback: {e}")
                    import traceback
                    traceback.print_exc()
                    await interaction.response.send_message(f"❌ Erro: {e}", ephemeral=True)
        
        class ProductSelectView(disnake.ui.View):
            def __init__(self, products):
                super().__init__(timeout=300)
                self.add_item(ProductSelect(products))
        
        # Criar embed
        embed = disnake.Embed(
            title="📦 Adicionar Estoque",
            description=f"Selecione o produto para adicionar códigos/keys.\n\n"
                       f"**Produtos com estoque gerenciado:** {len(products_with_stock)}",
            color=disnake.Color.blue()
        )
        
        view = ProductSelectView(products_with_stock)
        await inter.followup.send(embed=embed, view=view, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando /adicionar_estoque: {e}")
        import traceback
        traceback.print_exc()
        await inter.followup.send(f"❌ Erro: {e}", ephemeral=True)


# Executar o bot
if __name__ == "__main__":
    try:
        print("🚀 Iniciando bot...")
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")
        import traceback
        traceback.print_exc()
# Force deploy - 10/24/2025 17:16:33
# Force deploy - debug logs 10/24/2025 17:26:13
