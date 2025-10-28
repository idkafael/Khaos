import disnake
from typing import Optional
from models.guild_config_model import GuildConfigModel
from datetime import datetime

class LogSystem:
    """
    Sistema de logs centralizado do bot
    
    Níveis de log:
    - Nível 1: TUDO (tickets, pagamentos, entregas, cupons, VIP, etc)
    - Nível 2: Apenas PAGAMENTOS (pagamentos confirmados e entregas)
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.guild_config = GuildConfigModel()
    
    async def log(
        self,
        guild_id: int,
        event_type: str,
        title: str,
        description: str,
        user: Optional[disnake.Member] = None,
        fields: Optional[list] = None,
        color: int = 0x5865F2,
        thumbnail_url: Optional[str] = None
    ):
        """
        Envia log para o canal configurado
        
        Args:
            guild_id: ID do servidor
            event_type: Tipo do evento (ticket_created, payment_confirmed, etc)
            title: Título do embed
            description: Descrição do evento
            user: Usuário relacionado ao evento
            fields: Lista de dicts com name e value para adicionar ao embed
            color: Cor do embed
            thumbnail_url: URL da thumbnail
        """
        try:
            # Buscar configuração de logs
            log_config = await self.guild_config.get_log_config(guild_id)
            
            if not log_config:
                return  # Logs não configurados
            
            log_channel_id = log_config['log_channel_id']
            log_events = log_config.get('log_events', [])
            
            # Se log_events está vazio, logar tudo
            # Senão, verificar se este evento está na lista
            if log_events and event_type not in log_events:
                return  # Evento não está habilitado para log
            
            # Buscar canal
            log_channel = self.bot.get_channel(log_channel_id)
            
            if not log_channel:
                print(f"⚠️ Canal de logs {log_channel_id} não encontrado para servidor {guild_id}")
                return
            
            # Criar embed
            embed = disnake.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.utcnow()
            )
            
            # Adicionar informações do usuário
            if user:
                embed.set_author(
                    name=f"{user.name} ({user.id})",
                    icon_url=user.display_avatar.url if user.display_avatar else None
                )
            
            # Adicionar fields personalizados
            if fields:
                for field in fields:
                    embed.add_field(
                        name=field.get('name', 'Campo'),
                        value=field.get('value', 'N/A'),
                        inline=field.get('inline', True)
                    )
            
            # Adicionar thumbnail
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
            
            # Adicionar footer com tipo de evento
            embed.set_footer(text=f"Evento: {event_type}")
            
            # Enviar log
            # Workaround para erro de '_files' no disnake
            try:
                await log_channel.send(embed=embed)
            except AttributeError:
                # Se _files não existe, usar try-except para criar embed sem o atributo
                embed_copy = embed.__class__()
                embed_copy.title = embed.title
                embed_copy.description = embed.description
                embed_copy.color = embed.color
                embed_copy.timestamp = embed.timestamp
                for field in embed.fields:
                    embed_copy.add_field(name=field.name, value=field.value, inline=field.inline)
                if embed.footer:
                    embed_copy.set_footer(text=embed.footer.text)
                if embed.author:
                    embed_copy.set_author(name=embed.author.name, icon_url=embed.author.icon_url)
                if embed.thumbnail:
                    embed_copy.set_thumbnail(url=embed.thumbnail.url)
                await log_channel.send(embed=embed_copy)
            
        except Exception as e:
            print(f"❌ Erro ao enviar log: {e}")
            import traceback
            traceback.print_exc()
    
    async def log_ticket_created(self, guild_id: int, user: disnake.Member, product_name: str, product_price: float, channel: disnake.TextChannel):
        """Log de ticket de compra criado"""
        await self.log(
            guild_id=guild_id,
            event_type="ticket_created",
            title="🎫 Ticket de Compra Criado",
            description=f"Um novo ticket de compra foi aberto.",
            user=user,
            fields=[
                {'name': '🛍️ Produto', 'value': product_name, 'inline': True},
                {'name': '💰 Valor', 'value': f"R$ {product_price:.2f}", 'inline': True},
                {'name': '📺 Canal', 'value': channel.mention, 'inline': False}
            ],
            color=0x5865F2
        )
    
    async def log_support_ticket_created(self, guild_id: int, user: disnake.Member, category: str, channel: disnake.TextChannel):
        """Log de ticket de suporte criado"""
        await self.log(
            guild_id=guild_id,
            event_type="support_ticket_created",
            title="🆘 Ticket de Suporte Criado",
            description=f"Um novo ticket de suporte foi aberto.",
            user=user,
            fields=[
                {'name': '📋 Categoria', 'value': category, 'inline': True},
                {'name': '📺 Canal', 'value': channel.mention, 'inline': False}
            ],
            color=0xFFA500
        )
    
    async def log_payment_generated(self, guild_id: int, user: disnake.Member, product_name: str, amount: float, transaction_id: int):
        """Log de pagamento gerado"""
        await self.log(
            guild_id=guild_id,
            event_type="payment_generated",
            title="💳 Pagamento Gerado",
            description=f"QR Code Pix gerado com sucesso.",
            user=user,
            fields=[
                {'name': '🛍️ Produto', 'value': product_name, 'inline': True},
                {'name': '💰 Valor', 'value': f"R$ {amount:.2f}", 'inline': True},
                {'name': '🆔 Transação', 'value': f"#{transaction_id}", 'inline': True}
            ],
            color=0x0099FF
        )
    
    async def log_payment_confirmed(self, guild_id: int, user: disnake.Member, product_name: str, amount: float, transaction_id: int):
        """Log de pagamento confirmado"""
        # Garantir que amount não seja None
        if amount is None:
            amount = 0.0
        
        await self.log(
            guild_id=guild_id,
            event_type="payment_confirmed",
            title="✅ Pagamento Confirmado",
            description=f"💰 Pagamento via Pix confirmado com sucesso!",
            user=user,
            fields=[
                {'name': '🛍️ Produto', 'value': product_name, 'inline': True},
                {'name': '💵 Valor', 'value': f"R$ {amount:.2f}", 'inline': True},
                {'name': '🆔 Transação', 'value': f"#{transaction_id}", 'inline': True}
            ],
            color=0x00FF00
        )
    
    async def log_product_delivered(self, guild_id: int, user: disnake.Member, product_name: str, amount: float, channel: disnake.TextChannel):
        """Log de produto entregue"""
        # Garantir que amount não seja None
        if amount is None:
            amount = 0.0
        
        await self.log(
            guild_id=guild_id,
            event_type="product_delivered",
            title="📦 Produto Entregue",
            description=f"🎉 Produto entregue com sucesso!",
            user=user,
            fields=[
                {'name': '🛍️ Produto', 'value': product_name, 'inline': True},
                {'name': '💰 Valor Pago', 'value': f"R$ {amount:.2f}", 'inline': True},
                {'name': '📺 Canal', 'value': channel.mention, 'inline': False}
            ],
            color=0x00FF00
        )
    
    async def log_ticket_closed(self, guild_id: int, user: disnake.Member, closed_by: disnake.Member, product_name: Optional[str] = None):
        """Log de ticket fechado"""
        await self.log(
            guild_id=guild_id,
            event_type="ticket_closed",
            title="🔒 Ticket Fechado",
            description=f"Ticket foi fechado.",
            user=user,
            fields=[
                {'name': '👨‍💼 Fechado por', 'value': closed_by.mention, 'inline': True},
                {'name': '🛍️ Produto', 'value': product_name or 'Suporte', 'inline': True}
            ],
            color=0xFF0000
        )
    
    async def log_coupon_used(self, guild_id: int, user: disnake.Member, coupon_code: str, discount: float, product_name: str):
        """Log de cupom usado"""
        await self.log(
            guild_id=guild_id,
            event_type="coupon_used",
            title="🎟️ Cupom Utilizado",
            description=f"Um cupom de desconto foi aplicado.",
            user=user,
            fields=[
                {'name': '🎫 Cupom', 'value': coupon_code, 'inline': True},
                {'name': '💸 Desconto', 'value': f"R$ {discount:.2f}", 'inline': True},
                {'name': '🛍️ Produto', 'value': product_name, 'inline': True}
            ],
            color=0xFF6B9D
        )
    
    async def log_vip_activated(self, guild_id: int, user: disnake.Member, vip_role: str, duration_days: Optional[int], amount: float):
        """Log de VIP ativado"""
        duration_text = f"{duration_days} dias" if duration_days else "Vitalício"
        
        await self.log(
            guild_id=guild_id,
            event_type="vip_activated",
            title="👑 VIP Ativado",
            description=f"Assinatura VIP ativada com sucesso!",
            user=user,
            fields=[
                {'name': '⭐ Role', 'value': vip_role, 'inline': True},
                {'name': '⏰ Duração', 'value': duration_text, 'inline': True},
                {'name': '💰 Valor', 'value': f"R$ {amount:.2f}", 'inline': True}
            ],
            color=0xFFD700
        )
    
    async def log_vip_expired(self, guild_id: int, user: disnake.Member, vip_role: str):
        """Log de VIP expirado"""
        await self.log(
            guild_id=guild_id,
            event_type="vip_expired",
            title="⏰ VIP Expirado",
            description=f"Assinatura VIP expirou.",
            user=user,
            fields=[
                {'name': '⭐ Role', 'value': vip_role, 'inline': True}
            ],
            color=0xFF0000
        )
    
    async def log_stock_added(self, guild_id: int, admin: disnake.Member, product_name: str, quantity: int):
        """Log de estoque adicionado"""
        await self.log(
            guild_id=guild_id,
            event_type="stock_added",
            title="📦 Estoque Adicionado",
            description=f"Novos itens foram adicionados ao estoque.",
            user=admin,
            fields=[
                {'name': '🛍️ Produto', 'value': product_name, 'inline': True},
                {'name': '📊 Quantidade', 'value': f"{quantity} itens", 'inline': True}
            ],
            color=0x0099FF
        )
    
    async def log_product_created(self, guild_id: int, admin: disnake.Member, product_name: str, price: float, category: str):
        """Log de produto criado"""
        await self.log(
            guild_id=guild_id,
            event_type="product_created",
            title="➕ Produto Criado",
            description=f"Um novo produto foi adicionado ao servidor.",
            user=admin,
            fields=[
                {'name': '🛍️ Nome', 'value': product_name, 'inline': True},
                {'name': '💰 Preço', 'value': f"R$ {price:.2f}", 'inline': True},
                {'name': '📦 Categoria', 'value': category, 'inline': True}
            ],
            color=0x00FF00
        )

