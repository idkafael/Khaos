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

@bot.tree.command(name="setup_msg", description="[ADMIN] Criar mensagem embed personalizada")
@discord.app_commands.default_permissions(administrator=True)
async def setup_msg_slash(interaction: discord.Interaction):
    """Comando admin para criar mensagem embed via modal"""
    try:
        print(f"Comando setup_msg executado por {interaction.user.name}")
        
        from utils.ticket_views import SetupMessageModal
        print("SetupMessageModal importado com sucesso!")
        
        modal = SetupMessageModal()
        print("Modal criado com sucesso!")
        
        await interaction.response.send_modal(modal)
        print("Modal enviado com sucesso!")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            description="❌ Erro de importação no sistema de mensagens.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Erro no comando setup_msg: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            description="❌ Erro ao criar mensagem embed.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setup_suporte", description="[ADMIN] Configurar sistema de tickets de suporte")
@discord.app_commands.default_permissions(administrator=True)
async def setup_suporte_slash(interaction: discord.Interaction):
    """Comando admin para configurar sistema de tickets de suporte via modal"""
    try:
        print(f"Comando setup_suporte executado por {interaction.user.name}")
        
        from utils.ticket_views import SetupSupportModal
        print("SetupSupportModal importado com sucesso!")
        
        modal = SetupSupportModal()
        print("Modal de suporte criado com sucesso!")
        
        await interaction.response.send_modal(modal)
        print("Modal de suporte enviado com sucesso!")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            description="❌ Erro de importação no sistema de suporte.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Erro no comando setup_suporte: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            description="❌ Erro ao configurar sistema de suporte.",
            color=0x8B5CF6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="clear", aliases=["limpar", "apagar"])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 10):
    """Comando para apagar mensagens do chat
    
    Uso: !clear [número]
    Exemplo: !clear 50
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
        
    except discord.Forbidden:
        await ctx.send("❌ Não tenho permissão para apagar mensagens neste canal!", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"❌ Erro ao apagar mensagens: {e}", delete_after=5)
    except Exception as e:
        print(f"Erro no comando !clear: {e}")
        await ctx.send("❌ Ocorreu um erro ao apagar as mensagens.", delete_after=5)

@clear_messages.error
async def clear_error(ctx, error):
    """Handler de erros do comando clear"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando! (Necessário: Gerenciar Mensagens)", delete_after=5)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Uso correto: `!clear [número]` - Exemplo: `!clear 50`", delete_after=5)
    else:
        print(f"Erro no comando clear: {error}")

@bot.tree.command(name="status", description="Ver status do seu pagamento")
async def status_slash(interaction: discord.Interaction):
    """Comando para ver status do pagamento"""
    try:
        # Verificar se está em canal de ticket
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message("❌ Este comando só funciona em canais de ticket!", ephemeral=True)
            return
        
        # Buscar transação do usuário neste canal
        transaction_model = TransactionModel()
        transactions = await transaction_model.get_user_transactions(interaction.user.id)
        
        # Filtrar pela transação deste canal
        current_transaction = None
        for trans in transactions:
            if trans.get('delivery_channel_id') == interaction.channel.id:
                current_transaction = trans
                break
        
        if not current_transaction:
            await interaction.response.send_message("❌ Nenhuma transação encontrada neste canal.", ephemeral=True)
            return
        
        # Buscar produto
        product_model = ProductModel()
        product = await product_model.get_product_by_id(current_transaction['product_id'])
        
        status = current_transaction.get('status', 'pending')
        
        # Criar embed baseado no status
        if status == 'pending':
            # Pagamento pendente
            embed = discord.Embed(
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
                qr_file = discord.File(img_bytes, filename="qrcode.png")
                
                await interaction.response.send_message(embed=embed, file=qr_file, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        elif status == 'completed':
            # Pagamento confirmado e produto entregue
            embed = discord.Embed(
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
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif status == 'expired':
            embed = discord.Embed(
                title="⏰ Pagamento Expirado",
                description=f"O prazo para pagamento expirou.",
                color=0xff0000
            )
            embed.add_field(
                name="💡 Quer tentar novamente?",
                value="Clique no botão 'Criar Ticket' para gerar um novo pagamento.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="📊 Status do Pagamento",
                description=f"Status: **{status}**",
                color=0x3498db
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        print(f"Erro no comando status: {e}")
        import traceback
        traceback.print_exc()
        await interaction.response.send_message("❌ Erro ao buscar status do pagamento.", ephemeral=True)

@bot.tree.command(name="comprar", description="Comprar produto (use no canal do ticket)")
async def comprar_slash(interaction: discord.Interaction, produto: str):
    """Comando para comprar produto no canal do ticket"""
    try:
        # Verificar se está em canal de ticket
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message("❌ Este comando só funciona em canais de ticket!", ephemeral=True)
            return
        
        # Buscar produto por nome
        product_model = ProductModel()
        product = await product_model.get_product_by_name(produto)
        
        if not product:
            await interaction.response.send_message(f"❌ Produto '{produto}' não encontrado!", ephemeral=True)
            return
        
        # Buscar cupom do ticket (se houver)
        coupon_code = None
        coupon_data = None
        discount_amount = 0
        final_amount = product['price']
        split_config = None
        
        # Verificar se tem cupom no ticket
        ticket_data = active_tickets.get(interaction.user.id)
        if ticket_data and ticket_data.get('coupon_code'):
            coupon_code = ticket_data['coupon_code']
            
            # Validar cupom
            from models.coupon_model import CouponModel
            coupon_model = CouponModel()
            is_valid, message, coupon_data = await coupon_model.validate_coupon(
                coupon_code,
                interaction.user.id,
                product['price']
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
                await interaction.channel.send(
                    f"🎉 Cupom **{coupon_code}** aplicado! Desconto de {coupon_data['discount_percent']}% = R$ {discount_amount:.2f}"
                )
            else:
                # Cupom inválido - informar e continuar sem desconto
                await interaction.channel.send(f"⚠️ {message} - Continuando sem desconto.")
                coupon_data = None
        
        # Criar transação
        transaction_model = TransactionModel()
        transaction = await transaction_model.create_transaction(
            user_id=interaction.user.id,
            product_id=product['id'],
            amount=product['price'],
            discount_amount=discount_amount,
            final_amount=final_amount,
            coupon_id=coupon_data['id'] if coupon_data else None,
            status='pending'
        )
        
        if not transaction:
            await interaction.response.send_message("❌ Erro ao criar transação!", ephemeral=True)
            return
        
        # Gerar pagamento Pix com valor final
        payment_utils = PaymentUtils()
        payment_data = await payment_utils.create_pix_payment(
            amount=final_amount,  # Valor com desconto
            description=f"Compra: {product['name']}",
            customer_email=f"{interaction.user.name.lower().replace(' ', '')}@khaos.com",
            customer_name=interaction.user.display_name,
            split_config=split_config  # Passar split se houver
        )
        
        if payment_data:
            # Atualizar transação
            await transaction_model.update_transaction(transaction['id'], {
                'payment_id': payment_data.get('id'),
                'pix_code': payment_data.get('pix_code'),
                'qr_code': payment_data.get('qr_code'),
                'email': f"{interaction.user.name.lower().replace(' ', '')}@khaos.com"
            })
            
            # Registrar uso do cupom
            if coupon_data:
                from models.coupon_model import CouponModel
                coupon_model = CouponModel()
                await coupon_model.use_coupon(
                    coupon_data['id'],
                    interaction.user.id,
                    transaction['id'],
                    discount_amount
                )
            
            # Enviar pagamento
            embed = discord.Embed(
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
            
            await interaction.response.send_message(embed=embed)
            
        else:
            await interaction.response.send_message("❌ Erro ao gerar pagamento Pix!", ephemeral=True)
            
    except Exception as e:
        print(f"Erro no comando comprar: {e}")
        import traceback
        traceback.print_exc()
        await interaction.response.send_message("❌ Erro ao processar compra!", ephemeral=True)

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
        value="`/setup_ticket` :: ⚙️ Enviar mensagem de tickets (vendas)\n`/setup_suporte` :: 🆘 Enviar mensagem de suporte\n`/setup_msg` :: 📝 Criar mensagem embed\n`/close_ticket` :: 🔒 Fechar ticket manualmente\n`!clear [número]` :: 🗑️ Apagar mensagens do chat",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos de Estoque (Admin)",
        value="`/adicionar_estoque` :: 📦 Adicionar códigos/keys\n`/ver_estoque` :: 📊 Ver resumo do estoque\n`!adicionar_estoque` :: 📦 Adicionar via prefixo\n`!ver_estoque` :: 📊 Ver estoque via prefixo",
        inline=False
    )
    
    embed.add_field(
        name="» Comandos de Cupons (Admin)",
        value="`/criar_cupom` :: 🎟️ Criar novo cupom\n`/listar_cupons` :: 📋 Ver todos cupons\n`/cupom_stats` :: 📊 Estatísticas de cupom\n`/deletar_cupom` :: ❌ Desativar cupom",
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

# ========================================
# COMANDOS DE CUPONS (ADMIN)
# ========================================

@bot.tree.command(name="criar_cupom", description="[ADMIN] Criar novo cupom de desconto")
@discord.app_commands.default_permissions(administrator=True)
async def criar_cupom_slash(interaction: discord.Interaction):
    """Comando admin para criar cupom via modal"""
    try:
        from utils.ticket_views import CreateCouponModal
        
        modal = CreateCouponModal()
        await interaction.response.send_modal(modal)
        
    except Exception as e:
        print(f"Erro no comando criar_cupom: {e}")
        await interaction.response.send_message("❌ Erro ao abrir modal de cupom.", ephemeral=True)

@bot.tree.command(name="listar_cupons", description="[ADMIN] Listar todos os cupons")
@discord.app_commands.default_permissions(administrator=True)
async def listar_cupons_slash(interaction: discord.Interaction):
    """Lista todos os cupons ativos"""
    try:
        from models.coupon_model import CouponModel
        
        coupon_model = CouponModel()
        coupons = await coupon_model.get_all_coupons(active_only=True)
        
        if not coupons:
            await interaction.response.send_message("📋 Nenhum cupom cadastrado.", ephemeral=True)
            return
        
        embed = discord.Embed(
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando listar_cupons: {e}")
        import traceback
        traceback.print_exc()
        await interaction.response.send_message("❌ Erro ao listar cupons.", ephemeral=True)

@bot.tree.command(name="cupom_stats", description="[ADMIN] Ver estatísticas de um cupom")
@discord.app_commands.default_permissions(administrator=True)
async def cupom_stats_slash(interaction: discord.Interaction, codigo: str):
    """Mostra estatísticas de uso de um cupom"""
    try:
        from models.coupon_model import CouponModel
        
        coupon_model = CouponModel()
        stats = await coupon_model.get_coupon_stats(codigo)
        
        if not stats:
            await interaction.response.send_message(f"❌ Cupom '{codigo}' não encontrado.", ephemeral=True)
            return
        
        coupon = stats['coupon']
        
        embed = discord.Embed(
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando cupom_stats: {e}")
        import traceback
        traceback.print_exc()
        await interaction.response.send_message("❌ Erro ao buscar estatísticas.", ephemeral=True)

@bot.tree.command(name="deletar_cupom", description="[ADMIN] Desativar um cupom")
@discord.app_commands.default_permissions(administrator=True)
async def deletar_cupom_slash(interaction: discord.Interaction, codigo: str):
    """Desativa um cupom"""
    try:
        from models.coupon_model import CouponModel
        
        coupon_model = CouponModel()
        success, message = await coupon_model.delete_cupom(codigo)
        
        if success:
            embed = discord.Embed(
                title="✅ Cupom Desativado",
                description=message,
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
        
    except Exception as e:
        print(f"Erro no comando deletar_cupom: {e}")
        await interaction.response.send_message("❌ Erro ao deletar cupom.", ephemeral=True)

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
        
        # Criar embed principal
        embed = discord.Embed(
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
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando /produtos: {e}")
        embed = discord.Embed(
            description="❌ Erro ao carregar produtos. Tente novamente em alguns instantes.",
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
    
    # Inicializar inventory model
    from models.inventory_model import InventoryModel
    inventory_model = InventoryModel()
    await inventory_model.initialize()
    
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
    from discord.ext import tasks
    
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

# Comando para recarregar produtos
@bot.command(name='reload_products')
@commands.has_permissions(administrator=True)
async def reload_products(ctx):
    """Recarrega os produtos no banco de dados"""
    try:
        await ctx.send("🔄 Limpando produtos antigos...")
        
        # Limpar produtos existentes
        products = await product_model.get_all_products()
        deleted_count = 0
        for product in products:
            await product_model.delete_product(product['id'])
            deleted_count += 1
        
        await ctx.send(f"✅ {deleted_count} produtos antigos removidos!")
        
        # Carregar novos produtos
        await ctx.send("🔄 Carregando novos produtos...")
        await load_sample_products()
        
        # Verificar se foram carregados
        new_products = await product_model.get_all_products()
        await ctx.send(f"✅ {len(new_products)} novos produtos carregados!")
        
        # Listar os novos produtos
        for product in new_products:
            await ctx.send(f"📦 **{product['name']}** - R$ {product['price']:.2f}")
        
    except Exception as e:
        print(f"Erro ao recarregar produtos: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Erro ao recarregar produtos: {e}")

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
        embed = discord.Embed(
            title="➕ Adicionar Estoque",
            description="**Produtos disponíveis:**",
            color=0x3498db
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
                  f"`!add_stock_id <ID> <códigos>`\n\n"
                  "Exemplo:\n"
                  f"`!add_stock_id {products[0]['id']}`\n"
                  "Depois cole os códigos, um por linha.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Erro no comando !adicionar_estoque: {e}")
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
                      f"Quando terminar, envie `!done` ou aguarde 30 segundos.")
        
        # Esperar pelas mensagens do usuário
        codes = []
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        for _ in range(100):  # Máximo 100 códigos por vez
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=check)
                
                if msg.content.lower() in ['!done', 'done', 'pronto', '!pronto']:
                    break
                
                # Adicionar códigos
                lines = msg.content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('!'):
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
            embed = discord.Embed(
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
        embed = discord.Embed(
            title="📊 Resumo de Estoque",
            description="Status de estoque de todos os produtos",
            color=0x3498db
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
        embed = discord.Embed(
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

# Executar o bot
if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro ao iniciar o bot: {e}")
