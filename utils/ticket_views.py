import discord
from discord import ui
from typing import List, Dict, Optional
from models.product_model import ProductModel
from utils.ticket_manager import TicketManager
import asyncio

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

class ProductSelectView(ui.View):
    """View com select menu para escolher produto"""
    
    def __init__(self, products: List[Dict], select_menu: ui.Select):
        super().__init__(timeout=300)
        self.products = products
        self.add_item(select_menu)
    
    async def on_timeout(self):
        """Quando o timeout expira"""
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
    
    @ui.select(placeholder="Escolha um produto...")
    async def select_product(self, interaction: discord.Interaction, select: ui.Select):
        """Callback do select menu"""
        try:
            selected_product_id = int(select.values[0])
            selected_product = next(
                (p for p in self.products if p['id'] == selected_product_id), 
                None
            )
            
            if not selected_product:
                await interaction.response.send_message("❌ Produto não encontrado.", ephemeral=True)
                return
            
            # Criar ticket usando TicketManager
            ticket_manager = TicketManager()
            success, message = await ticket_manager.create_ticket(
                interaction.user, 
                interaction.guild, 
                selected_product
            )
            
            if success:
                await interaction.response.send_message(f"✅ {message}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            print(f"Erro ao processar seleção de produto: {e}")
            await interaction.response.send_message("❌ Erro ao criar ticket. Tente novamente.", ephemeral=True)

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
            from bot import active_tickets
            if interaction.user.id in active_tickets:
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
            
            # Criar select menu com produtos
            select_menu = ui.Select(
                placeholder="Escolha um produto...",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(
                        label=product['name'],
                        description=f"R$ {product['price']:.2f} - {product.get('description', 'Sem descrição')[:100]}",
                        value=str(product['id'])
                    )
                    for product in products
                ]
            )
            
            # Criar view com select menu
            view = ProductSelectView(products, select_menu)
            
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

class TicketChannelView(ui.View):
    """View para canais de ticket com botão de fechar"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())
