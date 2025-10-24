import discord
from datetime import datetime
from typing import Tuple, Optional
from config.config import Config

class TicketManager:
    """Gerenciador de tickets e canais privados"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.ticket_category_id = getattr(Config, 'TICKET_CATEGORY_ID', None)
        self.admin_role_id = getattr(Config, 'ADMIN_ROLE_ID', None)
        self.logs_channel_id = getattr(Config, 'TICKET_LOGS_CHANNEL_ID', None)
    
    async def create_ticket(self, user: discord.Member, guild: discord.Guild, product: dict, coupon_code: str = None) -> Tuple[bool, str]:
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
            
            # Enviar mensagem de boas-vindas primeiro
            await self._send_welcome_message(ticket_channel, user, product)
            
            # Armazenar informações do ticket APÓS enviar a mensagem
            bot.active_tickets[user.id] = {
                'channel_id': ticket_channel.id,
                'user_id': user.id,
                'product_id': product['id'],
                'product_name': product['name'],
                'coupon_code': coupon_code,  # Armazenar cupom
                'status': 'active',
                'created_at': datetime.now()
            }
            
            print(f"✅ Debug: Ticket adicionado ao active_tickets!")
            print(f"🔧 Debug: Usuário: {user.id}, Canal: {ticket_channel.id}")
            print(f"🔧 Debug: Total de tickets ativos: {len(bot.active_tickets)}")
            
            # Log da criação do ticket
            await self._log_ticket_creation(guild, user, product, ticket_channel)
            
            # LOG: Ticket de compra criado
            if self.bot and hasattr(self.bot, 'log_system'):
                try:
                    await self.bot.log_system.log_ticket_created(
                        guild_id=guild.id,
                        user=user,
                        product_name=product['name'],
                        product_price=product['price'],
                        channel=ticket_channel
                    )
                except Exception as log_err:
                    print(f"Erro ao enviar log de ticket criado: {log_err}")
            
            return True, f"Ticket criado com sucesso! Acesse {ticket_channel.mention}"
            
        except Exception as e:
            print(f"Erro ao criar ticket: {e}")
            return False, f"Erro ao criar ticket: {str(e)}"
    
    async def create_support_ticket(self, user: discord.Member, guild: discord.Guild, categoria: str = "Suporte") -> Tuple[bool, str]:
        """Cria um ticket de suporte (sem produto)"""
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
            
            # Criar canal de suporte com categoria no nome
            timestamp = datetime.now().strftime("%m%d%H%M")
            categoria_slug = categoria.lower().replace(' ', '-').replace('ã', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            channel_name = f"{categoria_slug}-{user.name.lower().replace(' ', '-')}-{timestamp}"
            
            ticket_channel = await guild.create_text_channel(
                channel_name,
                overwrites=overwrites,
                category=category
            )
            
            # Enviar mensagem de boas-vindas
            await self._send_support_welcome_message(ticket_channel, user, categoria)
            
            # Armazenar informações do ticket
            bot.active_tickets[user.id] = {
                'channel_id': ticket_channel.id,
                'user_id': user.id,
                'type': 'support',  # Tipo: suporte
                'categoria': categoria,  # Categoria do ticket
                'status': 'active',
                'created_at': datetime.now()
            }
            
            print(f"✅ Ticket de suporte criado: {channel_name} (Categoria: {categoria})")
            
            # LOG: Ticket de suporte criado
            if self.bot and hasattr(self.bot, 'log_system'):
                try:
                    await self.bot.log_system.log_support_ticket_created(
                        guild_id=guild.id,
                        user=user,
                        category=categoria,
                        channel=ticket_channel
                    )
                except Exception as log_err:
                    print(f"Erro ao enviar log de ticket de suporte criado: {log_err}")
            
            return True, f"Ticket de {categoria} criado! Acesse {ticket_channel.mention}"
            
        except Exception as e:
            print(f"Erro ao criar ticket de suporte: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Erro ao criar ticket de suporte: {str(e)}"
    
    async def _send_support_welcome_message(self, channel: discord.TextChannel, user: discord.Member, categoria: str = "Suporte"):
        """Envia mensagem de boas-vindas no canal de suporte"""
        from utils.ticket_views import TicketChannelView
        
        # Emojis por categoria
        emoji_map = {
            'parcerias': '🤝',
            'duvidas': '💡',
            'denuncias': '✅',
            'sorteios': '🎁',
            'suporte': '🆘'
        }
        
        categoria_lower = categoria.lower().replace('ú', 'u').replace('í', 'i').replace('ê', 'e')
        emoji = emoji_map.get(categoria_lower, '🆘')
        
        embed = discord.Embed(
            title=f"{emoji} Ticket de {categoria} Criado!",
            description=f"Olá {user.mention}! Bem-vindo ao seu ticket de **{categoria}**.",
            color=0x5865F2
        )
        
        embed.add_field(
            name="📝 Deixe sua Mensagem",
            value="Descreva detalhadamente seu problema ou dúvida abaixo.\n\n"
                  "**Deixe sua mensagem previamente para que quando um suporte veja possamos solucionar!**",
            inline=False
        )
        
        embed.add_field(
            name="💡 Dicas para um Atendimento Rápido",
            value="• Seja claro e objetivo\n"
                  "• Forneça detalhes do problema\n"
                  "• Envie prints se necessário\n"
                  "• Aguarde a resposta da equipe",
            inline=False
        )
        
        embed.set_footer(text="Nossa equipe está disponível 24/7 • Responderemos o mais breve possível")
        
        view = TicketChannelView()
        await channel.send(embed=embed, view=view)
    
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
            description=f"Olá {user.mention}! Bem-vindo ao seu ticket de compra.",
            color=0x00ff00
        )
        
        # Destacar o produto selecionado
        embed.add_field(
            name="🛍️ Produto Selecionado",
            value=f"╭─ **{product['name']}**\n"
                  f"├─ 💰 **Valor:** R$ {product['price']:.2f}\n"
                  f"├─ 📝 {product.get('description', 'Produto digital')}\n"
                  f"╰─ 📦 {product.get('category', 'Digital')}",
            inline=False
        )
        
        embed.add_field(
            name="🚀 Processo Automatizado",
            value="```diff\n"
                  "+ Produto selecionado\n"
                  "+ Ticket criado\n"
                  "~ Gerando pagamento Pix...\n"
                  "```\n"
                  "⏳ **Aguarde:** Estamos processando seu pedido...",
            inline=False
        )
        
        embed.add_field(
            name="⏳ Próximos Passos",
            value="1️⃣ Aguarde a geração automática do QR Code\n"
                  "2️⃣ **OU** clique no botão 💳 **Gerar Pagamento** abaixo\n"
                  "3️⃣ Pague via Pix\n"
                  "4️⃣ Receba o produto automaticamente",
            inline=False
        )
        
        embed.set_footer(
            text=f"Ticket #{channel.name} • Pagamento sendo gerado...",
            icon_url=user.display_avatar.url if user.display_avatar else None
        )
        
        view = TicketChannelView()
        await channel.send(embed=embed, view=view)
        
        # Gerar pagamento automaticamente - PRIMEIRA OPÇÃO
        await self._generate_automatic_payment(channel, user, product)
    
    async def _generate_automatic_payment(self, channel: discord.TextChannel, user: discord.Member, product: dict):
        """Gera pagamento automaticamente - PRIMEIRA OPÇÃO"""
        try:
            print(f"🔄 Gerando pagamento automático para {user.name} - {product['name']}")
            
            # Verificar se produto tem estoque ilimitado
            is_unlimited = product.get('unlimited_stock', False)
            guild_id = channel.guild.id
            
            # 1. Verificar estoque disponível (apenas para produtos gerenciados)
            inventory_id = None
            if not is_unlimited:
                from models.inventory_model import InventoryModel
                inventory_model = InventoryModel()
                
                stock_counts = await inventory_model.get_stock_count(product['id'], guild_id)
                print(f"📦 Estoque disponível: {stock_counts['available']} itens")
                
                if stock_counts['available'] == 0:
                    # Sem estoque disponível
                    embed = discord.Embed(
                        title="❌ Produto Esgotado",
                        description=f"Infelizmente o produto **{product['name']}** está temporariamente sem estoque.",
                        color=0xff0000
                    )
                    embed.add_field(
                        name="📬 Notificação",
                        value="Entre em contato com um administrador para saber quando teremos novos itens disponíveis.",
                        inline=False
                    )
                    await channel.send(embed=embed)
                    return
                
                # 2. Reservar item do estoque
                available_stock = await inventory_model.get_available_stock(product['id'], guild_id)
                if not available_stock:
                    await self._send_out_of_stock_message(channel, product)
                    return
                
                inventory_id = available_stock['id']
            else:
                print(f"♾️ Produto com estoque ilimitado - pulando verificação")
            
            # 3. Criar transação no banco
            from models.transaction_model import TransactionModel
            transaction_model = TransactionModel()
            
            transaction_data = {
                'user_id': user.id,
                'product_id': product['id'],
                'amount': product['price'],
                'status': 'pending',
                'delivery_channel_id': channel.id,
                'guild_id': guild_id
            }
            
            transaction = await transaction_model.create_transaction(**transaction_data)
            
            if not transaction:
                print(f"❌ Falha ao criar transação no banco de dados")
                await self._send_fallback_message(channel, user, product)
                return
            
            print(f"✅ Transação criada: #{transaction['id']}")
            
            # 4. Reservar o estoque para esta transação (apenas para produtos gerenciados)
            if not is_unlimited and inventory_id:
                from models.inventory_model import InventoryModel
                inventory_model = InventoryModel()
                
                reserved = await inventory_model.reserve_stock(
                    inventory_id,
                    user.id,
                    transaction['id']
                )
                
                if not reserved:
                    print(f"⚠️ Falha ao reservar estoque para transação #{transaction['id']}")
                else:
                    print(f"✅ Estoque reservado: Item #{inventory_id} para transação #{transaction['id']}")
                    # Atualizar transação com inventory_id
                    await transaction_model.update_transaction(transaction['id'], {
                        'inventory_id': inventory_id
                    })
            
            # 5. Gerar pagamento Pix
            from utils.payment_utils import PaymentUtils
            payment_utils = PaymentUtils()
            
            print(f"💳 Gerando pagamento Pix - Valor: R$ {product['price']:.2f}")
            
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
                
                print(f"✅ Pagamento gerado com sucesso! ID: {payment_data.get('id')}")
                
                # LOG: Pagamento gerado
                if self.bot and hasattr(self.bot, 'log_system'):
                    try:
                        await self.bot.log_system.log_payment_generated(
                            guild_id=channel.guild.id,
                            user=user,
                            product_name=product['name'],
                            amount=product['price'],
                            transaction_id=transaction['id']
                        )
                    except Exception as log_err:
                        print(f"Erro ao enviar log de pagamento gerado: {log_err}")
                
                # Enviar pagamento no canal
                await self._send_payment_message(channel, user, product, payment_data)
            else:
                print(f"❌ Falha ao gerar pagamento Pix")
                
                # Se falhar, liberar reserva e enviar instruções para usar /comprar
                if not is_unlimited and inventory_id:
                    from models.inventory_model import InventoryModel
                    inventory_model = InventoryModel()
                    await inventory_model.release_reservation(inventory_id)
                    print(f"🔄 Reserva liberada: Item #{inventory_id}")
                
                await self._send_fallback_message(channel, user, product)
                
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao gerar pagamento automático: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar enviar mensagem de erro ao usuário
            try:
                await self._send_fallback_message(channel, user, product)
            except Exception as fallback_error:
                print(f"❌ Falha ao enviar mensagem de fallback: {fallback_error}")
                
                # Última tentativa: mensagem simples
                try:
                    await channel.send(
                        f"{user.mention} ❌ Ocorreu um erro ao processar seu pedido. "
                        f"Por favor, use o comando `/comprar` para tentar novamente."
                    )
                except:
                    pass
    
    async def _send_out_of_stock_message(self, channel: discord.TextChannel, product: dict):
        """Envia mensagem de produto esgotado"""
        embed = discord.Embed(
            title="❌ Produto Esgotado",
            description=f"O produto **{product['name']}** está temporariamente sem estoque.",
            color=0xff0000
        )
        embed.add_field(
            name="📬 Reposição",
            value="Estamos trabalhando para repor o estoque em breve.\nEntre em contato com um administrador para mais informações.",
            inline=False
        )
        await channel.send(embed=embed)
    
    async def _send_fallback_message(self, channel: discord.TextChannel, user: discord.Member, product: dict):
        """Envia mensagem de fallback quando pagamento automático falha"""
        embed = discord.Embed(
            title="⚠️ Pagamento Automático Falhou",
            description="Não conseguimos gerar o pagamento automaticamente, mas você pode tentar novamente manualmente.",
            color=0xffa500
        )
        
        embed.add_field(
            name="🔧 Como Continuar",
            value=f"Digite o comando abaixo neste canal:\n```/comprar```\n\n"
                  f"✨ **Novo:** O bot identifica automaticamente o produto **{product['name']}** do seu ticket!",
            inline=False
        )
        
        embed.add_field(
            name="❓ Possíveis Causas",
            value="• Instabilidade na API de pagamento\n"
                  "• Problemas temporários de conexão\n"
                  "• Produto pode estar sem estoque",
            inline=False
        )
        
        embed.add_field(
            name="💡 Dica",
            value=f"Se o erro persistir, entre em contato com um administrador.",
            inline=False
        )
        
        embed.set_footer(text=f"Ticket de {user.name} • Suporte disponível 24/7")
        
        await channel.send(f"{user.mention}", embed=embed)
    
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
            name="🔢 Código Pix (Copiar e Colar)",
            value=f"```{payment_data.get('qr_code', 'N/A')}```",
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
        
        # Enviar QR Code como imagem se disponível
        if payment_data.get('qr_code'):
            try:
                import qrcode
                import io
                
                # Debug: Verificar QR Code
                print(f"🔧 Debug: QR Code data: {payment_data.get('qr_code', 'N/A')[:50]}...")
                
                # Gerar QR Code usando o código Pix
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(payment_data['qr_code'])
                qr.make(fit=True)
                
                # Criar imagem
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Converter para bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                qr_file = discord.File(img_bytes, filename="qrcode.png")
                print(f"🔧 Debug: QR Code gerado: {len(img_bytes.getvalue())} bytes")
                
                await channel.send(embed=embed, file=qr_file)
                print("✅ QR Code gerado e enviado como imagem!")
                
            except Exception as e:
                print(f"Erro ao gerar QR Code: {e}")
                await channel.send(embed=embed)
                await channel.send(f"📱 **QR Code:**\n```\n{payment_data.get('qr_code', 'N/A')}\n```")
        else:
            await channel.send(embed=embed)
            await channel.send(f"📱 **QR Code:**\n```\n{payment_data.get('qr_code', 'N/A')}\n```")
    
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
