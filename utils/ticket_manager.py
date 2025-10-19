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
            from bot import active_tickets
            if user.id in active_tickets:
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
            active_tickets[user.id] = {
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
            from bot import active_tickets
            
            # Encontrar ticket pelo canal
            ticket_user_id = None
            for user_id, ticket_data in active_tickets.items():
                if ticket_data['channel_id'] == channel.id:
                    ticket_user_id = user_id
                    break
            
            if not ticket_user_id:
                return False, "Ticket não encontrado ou já foi fechado."
            
            # Remover do active_tickets
            ticket_data = active_tickets.pop(ticket_user_id, None)
            
            # Log do fechamento
            await self._log_ticket_closure(channel.guild, ticket_user_id, admin, ticket_data)
            
            return True, f"Ticket fechado com sucesso por {admin.mention}."
            
        except Exception as e:
            print(f"Erro ao fechar ticket: {e}")
            return False, f"Erro ao fechar ticket: {str(e)}"
    
    async def _send_welcome_message(self, channel: discord.TextChannel, user: discord.Member, product: dict):
        """Envia mensagem de boas-vindas no canal do ticket"""
        from utils.ticket_views import TicketChannelView
        
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
            name="📋 Próximos Passos",
            value="1. Use `/comprar` para gerar o pagamento Pix\n2. Use `/status` para verificar o progresso\n3. Use `/ajuda` para ver todos os comandos",
            inline=False
        )
        
        embed.add_field(
            name="💳 Informações de Pagamento",
            value="• Pagamento via Pix (QR Code + Código)\n• Entrega automática após confirmação\n• Suporte 24/7 disponível",
            inline=False
        )
        
        embed.set_footer(text="Digite /ajuda para ver todos os comandos disponíveis")
        
        view = TicketChannelView()
        await channel.send(embed=embed, view=view)
    
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
