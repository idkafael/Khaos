import discord
from datetime import datetime
from typing import Tuple, Optional
from config.config import Config

class TicketManager:
    """Gerenciador de tickets e canais privados"""
    
    def __init__(self):
        self.ticket_category_id = getattr(Config, 'TICKET_CATEGORY_ID', None)
        self.admin_role_id = getattr(Config, 'ADMIN_ROLE_ID', None)
        self.logs_channel_id = getattr(Config, 'TICKET_LOGS_CHANNEL_ID', None)
    
    async def create_ticket(self, user: discord.Member, guild: discord.Guild, product: dict) -> Tuple[bool, str]:
        """Cria um novo ticket (canal privado) para o usuário"""
        try:
            # Verificar se usuário já tem ticket ativo
            import bot
            if user.id in bot.active_tickets:
                return False, "Você já possui um ticket ativo."
            
            # Encontrar categoria de tickets (se configurada)
            category = None
            if self.ticket_category_id:
                category = discord.utils.get(guild.categories, id=self.ticket_category_id)
            
            # Configurar permissões do canal
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
            }
            
            # Adicionar permissões para admin role se configurado
            if self.admin_role_id:
                admin_role = discord.utils.get(guild.roles, id=self.admin_role_id)
                if admin_role:
                    overwrites[admin_role] = discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=True, 
                        manage_messages=True
                    )
            
            # Criar canal de ticket
            timestamp = datetime.now().strftime("%m%d%H%M")
            channel_name = f"ticket-{user.name.lower().replace(' ', '-')}-{timestamp}"
            
            ticket_channel = await guild.create_text_channel(
                channel_name,
                overwrites=overwrites,
                category=category
            )
            
            # Armazenar informações do ticket
            bot.active_tickets[user.id] = {
                'channel_id': ticket_channel.id,
                'user_id': user.id,
                'product_id': product['id'],
                'product_name': product['name'],
                'status': 'active',
                'created_at': datetime.now()
            }
            
            # Enviar mensagem de boas-vindas
            await self._send_welcome_message(ticket_channel, user, product)
            
            # Log da criação do ticket
            await self._log_ticket_creation(guild, user, product, ticket_channel)
            
            return True, f"Ticket criado com sucesso! Acesse {ticket_channel.mention}"
            
        except Exception as e:
            print(f"Erro ao criar ticket: {e}")
            return False, f"Erro ao criar ticket: {str(e)}"
    
    async def close_ticket(self, channel: discord.TextChannel, admin: discord.Member) -> Tuple[bool, str]:
        """Fecha um ticket (remove do active_tickets)"""
        try:
            import bot
            
            print(f"🔧 Debug: Tentando fechar ticket no canal {channel.name} (ID: {channel.id})")
            print(f"🔧 Debug: Active tickets atual: {len(bot.active_tickets)} tickets")
            print(f"🔧 Debug: Tickets ativos: {list(bot.active_tickets.keys())}")
            
            # Encontrar ticket pelo canal
            ticket_user_id = None
            for user_id, ticket_data in bot.active_tickets.items():
                print(f"🔧 Debug: Verificando ticket do usuário {user_id} - Canal ID: {ticket_data['channel_id']}")
                if ticket_data['channel_id'] == channel.id:
                    ticket_user_id = user_id
                    print(f"🔧 Debug: Ticket encontrado! Usuário: {ticket_user_id}")
                    break
            
            if not ticket_user_id:
                print(f"❌ Debug: Ticket não encontrado para o canal {channel.id}")
                return False, "Ticket não encontrado ou já foi fechado."
            
            # Remover do active_tickets
            ticket_data = bot.active_tickets.pop(ticket_user_id, None)
            print(f"✅ Debug: Ticket removido do active_tickets. Usuário: {ticket_user_id}")
            
            # Log do fechamento
            await self._log_ticket_closure(channel.guild, ticket_user_id, admin, ticket_data)
            
            return True, f"Ticket fechado com sucesso por {admin.mention}."
            
        except Exception as e:
            print(f"Erro ao fechar ticket: {e}")
            return False, f"Erro ao fechar ticket: {str(e)}"
    
    async def _send_welcome_message(self, channel: discord.TextChannel, user: discord.Member, product: dict):
        """Envia mensagem de boas-vindas no canal do ticket e gera pagamento automaticamente"""
        from utils.ticket_views import TicketChannelView
        from utils.payment_utils import PaymentUtils
        from models.transaction_model import TransactionModel
        
        embed = discord.Embed(
            title="🎫 Ticket de Compra Criado!",
            description=f"Olá {user.mention}! Bem-vindo ao nosso sistema de vendas.",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🛍️ Produto Selecionado",
            value=f"**{product['name']}**\nR$ {product['price']:.2f}",
            inline=False
        )
        
        embed.add_field(
            name="🚀 Processo Automatizado",
            value="✅ Produto selecionado\n🔄 Gerando pagamento Pix...\n⏳ Aguarde alguns segundos",
            inline=False
        )
        
        embed.set_footer(text="Pagamento sendo gerado automaticamente...")
        
        view = TicketChannelView()
        await channel.send(embed=embed, view=view)
        
        # Gerar pagamento automaticamente
        try:
            print(f"🔄 Gerando pagamento automático para {user.name} - {product['name']}")
            
            # Criar transação no banco
            transaction_model = TransactionModel()
            transaction = await transaction_model.create_transaction(
                user_id=user.id,
                product_id=product['id'],
                amount=product['price'],
                status='pending'
            )
            
            if not transaction:
                await channel.send("❌ Erro ao criar transação. Tente novamente.")
                return
            
            # Gerar pagamento Pix
            payment_utils = PaymentUtils()
            payment_data = await payment_utils.create_pix_payment(
                amount=product['price'],
                description=f"Compra: {product['name']}",
                customer_email=f"{user.name.lower().replace(' ', '')}@khaos.com",
                customer_name=user.display_name
            )
            
            if payment_data:
                # Atualizar transação com dados do pagamento
                await transaction_model.update_transaction(transaction['id'], {
                    'payment_id': payment_data.get('id'),
                    'pix_code': payment_data.get('pix_code'),
                    'qr_code': payment_data.get('qr_code'),
                    'email': f"{user.name.lower().replace(' ', '')}@khaos.com"
                })
                
                # Enviar pagamento no canal
                await self._send_payment_message(channel, user, product, payment_data)
            else:
                await channel.send("❌ Erro ao gerar pagamento Pix. Tente novamente.")
                
        except Exception as e:
            print(f"Erro ao gerar pagamento automático: {e}")
            await channel.send("❌ Erro ao gerar pagamento. Use `/comprar` para tentar novamente.")
    
    async def _send_payment_message(self, channel: discord.TextChannel, user: discord.Member, product: dict, payment_data: dict):
        """Envia mensagem com dados do pagamento Pix"""
        embed = discord.Embed(
            title="💳 Pagamento Pix Gerado!",
            description=f"**Produto:** {product['name']}\n**Valor:** R$ {product['price']:.2f}",
            color=0x00ff00
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
        
        embed.add_field(
            name="🚀 Entrega",
            value="✅ **Automática** após confirmação do pagamento\n📧 Produto será entregue neste canal",
            inline=False
        )
        
        embed.set_footer(text="Use /status para verificar o progresso do pagamento")
        
        # Enviar QR Code se disponível
        if payment_data.get('qr_code'):
            try:
                await channel.send(embed=embed)
                await channel.send(f"📱 **QR Code:**\n```\n{payment_data['qr_code']}\n```")
            except Exception as e:
                print(f"Erro ao enviar QR Code: {e}")
                await channel.send(embed=embed)
        else:
            await channel.send(embed=embed)
    
    async def _log_ticket_creation(self, guild: discord.Guild, user: discord.Member, product: dict, channel: discord.TextChannel):
        """Log da criação do ticket"""
        if not self.logs_channel_id:
            return
        
        try:
            logs_channel = guild.get_channel(self.logs_channel_id)
            if not logs_channel:
                return
            
            embed = discord.Embed(
                title="🎫 Novo Ticket Criado",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="👤 Usuário", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="🛍️ Produto", value=product['name'], inline=True)
            embed.add_field(name="💰 Valor", value=f"R$ {product['price']:.2f}", inline=True)
            embed.add_field(name="📺 Canal", value=channel.mention, inline=True)
            
            await logs_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao logar criação de ticket: {e}")
    
    async def _log_ticket_closure(self, guild: discord.Guild, user_id: int, admin: discord.Member, ticket_data: dict):
        """Log do fechamento do ticket"""
        if not self.logs_channel_id:
            return
        
        try:
            logs_channel = guild.get_channel(self.logs_channel_id)
            if not logs_channel:
                return
            
            user = guild.get_member(user_id)
            user_mention = user.mention if user else f"<@{user_id}>"
            
            embed = discord.Embed(
                title="🔒 Ticket Fechado",
                color=0xff0000,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="👤 Usuário", value=user_mention, inline=True)
            embed.add_field(name="👨‍💼 Admin", value=admin.mention, inline=True)
            embed.add_field(name="🛍️ Produto", value=ticket_data.get('product_name', 'N/A'), inline=True)
            
            await logs_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao logar fechamento de ticket: {e}")
    
    async def send_ticket_embed(self, channel: discord.TextChannel) -> bool:
        """Envia embed com botão para criar tickets"""
        try:
            from utils.ticket_views import TicketView
            
            embed = discord.Embed(
                title="🛒 Sistema de Vendas",
                description="Clique no botão abaixo para criar um ticket de compra e escolher seu produto!",
                color=0x0099ff
            )
            
            embed.add_field(
                name="📋 Como Funciona",
                value="1. Clique em 'Criar Ticket de Compra'\n2. Escolha o produto desejado\n3. Acesse seu canal privado\n4. Use `/comprar` para gerar pagamento",
                inline=False
            )
            
            embed.add_field(
                name="💳 Pagamento",
                value="• Pix com QR Code e código\n• Entrega automática\n• Suporte completo",
                inline=False
            )
            
            embed.set_footer(text="Sistema de tickets automático • Suporte 24/7")
            
            view = TicketView()
            await channel.send(embed=embed, view=view)
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar embed de ticket: {e}")
            return False
