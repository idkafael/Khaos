import discord
from discord import ui
from typing import List, Dict, Optional
from models.product_model import ProductModel
from utils.ticket_manager import TicketManager
import asyncio

class SetupMessageModal(ui.Modal):
    """Modal para criar mensagens embed personalizadas sem botões"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Criar Mensagem Embed", timeout=300)
        self.add_item(ui.TextInput(
            label="Título", 
            placeholder="Ex: Bem-vindo ao Servidor!", 
            default="",
            max_length=256,
            required=False
        ))
        self.add_item(ui.TextInput(
            label="Descrição", 
            placeholder="Escreva o conteúdo principal da mensagem...", 
            default="",
            style=discord.TextStyle.long,
            max_length=4000,
            required=True
        ))
        self.add_item(ui.TextInput(
            label="URL da Imagem", 
            placeholder="Cole o link da imagem (opcional)", 
            default="",
            required=False,
            max_length=500
        ))
        self.add_item(ui.TextInput(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #0099ff ou 0x0099ff", 
            default="#0099ff",
            max_length=10
        ))
        self.add_item(ui.TextInput(
            label="Rodapé (Footer)", 
            placeholder="Texto no rodapé (opcional)", 
            default="",
            required=False,
            max_length=100
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a criação da mensagem embed"""
        try:
            print(f"Modal de mensagem submetido por {interaction.user.name}")
            titulo = self.children[0].value.strip()
            descricao = self.children[1].value.strip()
            url_imagem = self.children[2].value.strip()
            cor_hex = self.children[3].value.strip()
            rodape = self.children[4].value.strip()
            
            print(f"Valores: titulo={titulo}, descricao={descricao[:50]}..., cor={cor_hex}")
            
            # Converter cor hex para int
            try:
                cor_hex = cor_hex.strip().lower()
                
                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]
                
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                
                cor_int = int(cor_hex, 16)
                print(f"Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0x0099ff
            
            # Criar embed
            embed = discord.Embed(
                description=descricao,
                color=cor_int
            )
            
            # Adicionar título se fornecido
            if titulo:
                embed.title = titulo
            
            # Adicionar imagem se fornecida
            if url_imagem and url_imagem.startswith(('http://', 'https://')):
                try:
                    embed.set_image(url=url_imagem)
                    print(f"Imagem adicionada: {url_imagem}")
                except Exception as e:
                    print(f"Erro ao adicionar imagem: {e}")
            
            # Adicionar rodapé se fornecido
            if rodape:
                embed.set_footer(text=rodape)
            
            # Enviar mensagem embed (sem view/botões)
            await interaction.response.send_message(embed=embed)
            print("Mensagem embed criada com sucesso")
            
        except Exception as e:
            print(f"Erro ao criar mensagem embed: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao criar mensagem embed.", ephemeral=True)

class SetupTicketModal(ui.Modal):
    """Modal para configurar o sistema de tickets"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Configurar Sistema de Tickets", timeout=300)
        self.add_item(ui.TextInput(
            label="Headline", 
            placeholder="Ex: Sistema de Vendas Automatizado", 
            default="🛒 Sistema de Vendas Automatizado",
            max_length=100
        ))
        self.add_item(ui.TextInput(
            label="Descrição", 
            placeholder="Ex: Clique no botão abaixo para criar um ticket de compra", 
            default="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            style=discord.TextStyle.long,
            max_length=1000
        ))
        self.add_item(ui.TextInput(
            label="Nome do Botão", 
            placeholder="Ex: Criar Ticket de Compra", 
            default="Criar Ticket de Compra",
            max_length=80
        ))
        self.add_item(ui.TextInput(
            label="URL da Imagem", 
            placeholder="Cole o link da imagem ou envie uma imagem no chat", 
            default="",
            required=False,
            max_length=500
        ))
        self.add_item(ui.TextInput(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #0099ff ou 0x0099ff", 
            default="#0099ff",
            max_length=10
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a configuração do sistema de tickets"""
        try:
            print(f"Modal submetido por {interaction.user.name}")
            headline = self.children[0].value
            descricao = self.children[1].value
            nome_botao = self.children[2].value
            url_imagem = self.children[3].value.strip()
            cor_hex = self.children[4].value.strip()
            
            print(f"Valores: {headline}, {descricao}, {nome_botao}, {url_imagem}, {cor_hex}")
            
            # Converter cor hex para int
            try:
                # Limpar a string de cor
                cor_hex = cor_hex.strip().lower()
                
                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]  # Remove #
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]  # Remove 0x
                
                # Garantir que tem 6 caracteres
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                
                cor_int = int(cor_hex, 16)
                print(f"Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0x0099ff  # Azul padrão
            
            # Criar embed com as configurações
            embed = discord.Embed(
                title=headline,
                description=descricao,
                color=cor_int
            )
            
            # Adicionar imagem se fornecida
            if url_imagem and url_imagem.startswith(('http://', 'https://')):
                try:
                    embed.set_image(url=url_imagem)
                    print(f"Imagem adicionada: {url_imagem}")
                except Exception as e:
                    print(f"Erro ao adicionar imagem: {e}")
            elif url_imagem:
                print(f"URL de imagem inválida: {url_imagem}")
            
            embed.add_field(
                name="🚀 Como Funciona?",
                value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
                inline=False
            )
            embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")
            
            # Criar view com botão personalizado
            view = TicketView(nome_botao)
            
            await interaction.response.send_message(embed=embed, view=view)
            print("Modal processado com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar sistema de tickets: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao configurar sistema de tickets.", ephemeral=True)

class CouponInputModal(ui.Modal):
    """Modal para coletar código de cupom (opcional)"""
    
    def __init__(self, user, guild, product):
        super().__init__(title="Cupom de Desconto (Opcional)", timeout=180)
        self.user = user
        self.guild = guild
        self.product = product
        
        self.add_item(ui.TextInput(
            label="Código do Cupom",
            placeholder="Digite o código do cupom ou deixe em branco",
            required=False,
            max_length=50
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa o cupom e cria o ticket"""
        try:
            coupon_code = self.children[0].value.strip() if self.children[0].value else None
            
            # Criar ticket com cupom
            ticket_manager = TicketManager()
            success, message = await ticket_manager.create_ticket(
                self.user,
                self.guild,
                self.product,
                coupon_code=coupon_code
            )
            
            if success:
                await interaction.response.send_message(f"✅ {message}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            print(f"Erro ao processar cupom: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao criar ticket.", ephemeral=True)

class ProductSelect(ui.Select):
    """Select menu personalizado para escolher produto"""
    
    def __init__(self, products: List[Dict], options: List[discord.SelectOption]):
        super().__init__(
            placeholder="Escolha um produto...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.products = products
    
    async def callback(self, interaction: discord.Interaction):
        """Callback do select menu - abre modal para cupom"""
        try:
            selected_product_id = int(self.values[0])
            selected_product = next(
                (p for p in self.products if p['id'] == selected_product_id), 
                None
            )
            
            if not selected_product:
                await interaction.response.send_message("❌ Produto não encontrado.", ephemeral=True)
                return
            
            # Abrir modal para coletar cupom
            modal = CouponInputModal(interaction.user, interaction.guild, selected_product)
            await interaction.response.send_modal(modal)
                
        except Exception as e:
            print(f"Erro ao processar seleção de produto: {e}")
            import traceback
            traceback.print_exc()
            try:
                await interaction.response.send_message("❌ Erro ao criar ticket. Tente novamente.", ephemeral=True)
            except discord.errors.NotFound:
                pass

class ProductSelectView(ui.View):
    """View com select menu para escolher produto"""
    
    def __init__(self, products: List[Dict]):
        super().__init__(timeout=300)
        self.products = products
        
        # Criar select menu diretamente aqui
        print(f"🔧 Debug: Criando select menu com {len(products)} produtos")
        
        # Verificar se há produtos
        if not products:
            print("❌ Debug: Nenhum produto para criar select menu")
            return
            
        # Criar opções do select
        options = []
        for i, product in enumerate(products):
            option = discord.SelectOption(
                label=product['name'],
                description=f"R$ {product['price']:.2f} - {product.get('description', 'Sem descrição')[:50]}",
                value=str(product['id'])
            )
            options.append(option)
            print(f"🔧 Debug: Opção {i+1}: {product['name']} - {product['id']}")
        
        print(f"🔧 Debug: Total de opções criadas: {len(options)}")
        
        select_menu = ProductSelect(products, options)
        self.add_item(select_menu)
    
    async def on_timeout(self):
        """Quando o timeout expira"""
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class TicketButton(ui.Button):
    """Botão para criar ticket que abre o modal"""
    
    def __init__(self, nome_botao="Criar Ticket de Compra"):
        super().__init__(
            label=f"🛒 {nome_botao}",
            style=discord.ButtonStyle.primary,
            emoji="🎫",
            custom_id="create_ticket_button"
        )
        self.product_model = ProductModel()
    
    async def callback(self, interaction: discord.Interaction):
        """Callback do botão - carrega produtos e abre modal"""
        try:
            # Debug: Verificar configurações
            from config.config import Config
            print(f"🔧 Debug: SUPABASE_URL: {Config.SUPABASE_URL[:20]}...")
            print(f"🔧 Debug: SUPABASE_KEY: {Config.SUPABASE_KEY[:20]}...")
            
            # Verificar se usuário já tem ticket ativo
            import bot
            if interaction.user.id in bot.active_tickets:
                await interaction.response.send_message(
                    "❌ Você já possui um ticket ativo. Use o canal do seu ticket para continuar.",
                    ephemeral=True
                )
                return
            
            # Carregar produtos disponíveis
            print(f"🔧 Debug: Tentando carregar produtos...")
            products = await self.product_model.get_all_products()
            print(f"🔧 Debug: Produtos carregados: {len(products) if products else 0}")
            
            if not products:
                await interaction.response.send_message(
                    "❌ Nenhum produto disponível no momento.",
                    ephemeral=True
                )
                return
            
            # Criar view com select menu
            view = ProductSelectView(products)
            
            embed = discord.Embed(
                title="🛍️ Escolha seu Produto",
                description="Selecione o produto que deseja comprar:",
                color=0x0099ff
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"❌ Erro no callback do botão de ticket: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Erro ao carregar produtos. Tente novamente.",
                ephemeral=True
            )

class TicketView(ui.View):
    """View persistente com botão de criar ticket"""
    
    def __init__(self, nome_botao="Criar Ticket de Compra"):
        super().__init__(timeout=None)
        self.add_item(TicketButton(nome_botao))

class CloseTicketButton(ui.Button):
    """Botão para admin fechar ticket"""
    
    def __init__(self):
        super().__init__(
            label="🔒 Fechar Ticket",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            custom_id="close_ticket_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback para fechar ticket"""
        try:
            # Verificar se é admin
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Apenas administradores podem fechar tickets.",
                    ephemeral=True
                )
                return
            
            # Verificar se é canal de ticket
            if not interaction.channel.name.startswith('ticket-'):
                await interaction.response.send_message(
                    "❌ Este comando só pode ser usado em canais de ticket.",
                    ephemeral=True
                )
                return
            
            # Fechar ticket
            ticket_manager = TicketManager()
            success, message = await ticket_manager.close_ticket(
                interaction.channel, 
                interaction.user
            )
            
            if success:
                await interaction.response.send_message(f"✅ {message}")
                # Deletar canal após 5 segundos
                await asyncio.sleep(5)
                await interaction.channel.delete()
            else:
                await interaction.response.send_message(f"❌ {message}")
                
        except Exception as e:
            print(f"Erro ao fechar ticket: {e}")
            await interaction.response.send_message(
                "❌ Erro ao fechar ticket. Tente novamente.",
                ephemeral=True
            )

class CreateCouponModal(ui.Modal):
    """Modal para criar cupom"""
    
    def __init__(self):
        super().__init__(title="Criar Novo Cupom", timeout=300)
        
        self.add_item(ui.TextInput(
            label="Código do Cupom",
            placeholder="Ex: PRIMEIRACOMPRA",
            max_length=50,
            required=True
        ))
        
        self.add_item(ui.TextInput(
            label="Desconto (%)",
            placeholder="Ex: 10 para 10%",
            max_length=5,
            required=True
        ))
        
        self.add_item(ui.TextInput(
            label="Limite de Usos (0 = ilimitado)",
            placeholder="Ex: 100",
            default="0",
            max_length=10,
            required=False
        ))
        
        self.add_item(ui.TextInput(
            label="Um uso por usuário? (sim/nao)",
            placeholder="sim ou nao",
            default="nao",
            max_length=3,
            required=False
        ))
        
        self.add_item(ui.TextInput(
            label="Data Expiração (DD/MM/YYYY ou vazio)",
            placeholder="31/12/2025",
            required=False,
            max_length=10
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa criação do cupom"""
        try:
            from models.coupon_model import CouponModel
            from datetime import datetime
            
            code = self.children[0].value.upper().strip()
            discount = float(self.children[1].value.strip())
            max_uses = int(self.children[2].value.strip()) if self.children[2].value.strip() and self.children[2].value.strip() != "0" else None
            one_per_user = self.children[3].value.strip().lower() == "sim"
            expires_str = self.children[4].value.strip()
            
            # Validar desconto
            if discount < 1 or discount > 100:
                await interaction.response.send_message("❌ Desconto deve estar entre 1% e 100%!", ephemeral=True)
                return
            
            # Processar data de expiração
            expires_at = None
            if expires_str:
                try:
                    expires_at = datetime.strptime(expires_str, "%d/%m/%Y").isoformat()
                except:
                    await interaction.response.send_message("❌ Data inválida! Use formato DD/MM/YYYY", ephemeral=True)
                    return
            
            # Criar cupom
            coupon_data = {
                'code': code,
                'discount_percent': discount,
                'max_uses': max_uses,
                'one_per_user': one_per_user,
                'expires_at': expires_at,
                'created_by': interaction.user.id,
                'active': True
            }
            
            coupon_model = CouponModel()
            success, message = await coupon_model.create_coupon(coupon_data)
            
            if success:
                embed = discord.Embed(
                    title="✅ Cupom Criado!",
                    description=f"Cupom **{code}** criado com sucesso!",
                    color=0x00ff00
                )
                embed.add_field(name="Desconto", value=f"{discount}%", inline=True)
                embed.add_field(name="Limite", value=str(max_uses) if max_uses else "Ilimitado", inline=True)
                embed.add_field(name="Um por usuário", value="Sim" if one_per_user else "Não", inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Valores inválidos! Verifique desconto e limite.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao criar cupom: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao criar cupom.", ephemeral=True)

class SetupSupportModal(ui.Modal):
    """Modal para configurar o sistema de tickets de suporte"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Configurar Tickets de Suporte", timeout=300)
        self.add_item(ui.TextInput(
            label="Título da Mensagem", 
            placeholder="Ex: Precisa de Ajuda?", 
            default="🆘 Precisa de Ajuda?",
            max_length=100
        ))
        self.add_item(ui.TextInput(
            label="Descrição", 
            placeholder="Ex: Clique no botão abaixo para abrir um ticket de suporte", 
            default="Clique no botão abaixo para abrir um ticket de suporte. Nossa equipe responderá o mais breve possível!",
            style=discord.TextStyle.long,
            max_length=1000
        ))
        self.add_item(ui.TextInput(
            label="Nome do Botão", 
            placeholder="Ex: Abrir Ticket de Suporte", 
            default="Abrir Ticket de Suporte",
            max_length=80
        ))
        self.add_item(ui.TextInput(
            label="URL da Imagem", 
            placeholder="Cole o link da imagem (opcional)", 
            default="",
            required=False,
            max_length=500
        ))
        self.add_item(ui.TextInput(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #ff6b6b ou 0xff6b6b", 
            default="#ff6b6b",
            max_length=10
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a configuração do sistema de tickets de suporte"""
        try:
            print(f"Modal de suporte submetido por {interaction.user.name}")
            titulo = self.children[0].value
            descricao = self.children[1].value
            nome_botao = self.children[2].value
            url_imagem = self.children[3].value.strip()
            cor_hex = self.children[4].value.strip()
            
            # Converter cor hex para int
            try:
                cor_hex = cor_hex.strip().lower()
                
                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]
                
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                
                cor_int = int(cor_hex, 16)
                print(f"Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0xff6b6b  # Vermelho padrão
            
            # Criar embed
            embed = discord.Embed(
                title=titulo,
                description=descricao,
                color=cor_int
            )
            
            # Adicionar imagem se fornecida
            if url_imagem and url_imagem.startswith(('http://', 'https://')):
                try:
                    embed.set_image(url=url_imagem)
                    print(f"Imagem adicionada: {url_imagem}")
                except Exception as e:
                    print(f"Erro ao adicionar imagem: {e}")
            
            embed.add_field(
                name="📋 Como Funciona?",
                value="1. Clique no botão abaixo\n2. Um canal privado será criado para você\n3. Descreva seu problema ou dúvida\n4. Aguarde o atendimento da equipe",
                inline=False
            )
            embed.set_footer(text="Suporte 24/7 • Responderemos em breve")
            
            # Criar view com botão de suporte
            view = SupportTicketView(nome_botao)
            
            await interaction.response.send_message(embed=embed, view=view)
            print("Modal de suporte processado com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar sistema de suporte: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao configurar sistema de suporte.", ephemeral=True)

class SupportTicketButton(ui.Button):
    """Botão para criar ticket de suporte"""
    
    def __init__(self, nome_botao="Abrir Ticket de Suporte"):
        super().__init__(
            label=nome_botao,
            style=discord.ButtonStyle.danger,
            emoji="🆘",
            custom_id="create_support_ticket_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback do botão - cria ticket de suporte direto"""
        try:
            # Verificar se usuário já tem ticket ativo
            import bot
            if interaction.user.id in bot.active_tickets:
                await interaction.response.send_message(
                    "❌ Você já possui um ticket ativo. Use o canal do seu ticket para continuar.",
                    ephemeral=True
                )
                return
            
            # Criar ticket de suporte direto (sem produto)
            ticket_manager = TicketManager()
            success, message = await ticket_manager.create_support_ticket(
                interaction.user,
                interaction.guild
            )
            
            if success:
                await interaction.response.send_message(f"✅ {message}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            print(f"❌ Erro no callback do botão de suporte: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Erro ao criar ticket de suporte. Tente novamente.",
                ephemeral=True
            )

class SupportTicketView(ui.View):
    """View persistente com botão de criar ticket de suporte"""
    
    def __init__(self, nome_botao="Abrir Ticket de Suporte"):
        super().__init__(timeout=None)
        self.add_item(SupportTicketButton(nome_botao))

class TicketChannelView(ui.View):
    """View para canais de ticket com botão de fechar"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())
