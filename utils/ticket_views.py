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
        self.add_item(ui.InputText(
            label="Headline", 
            placeholder="Ex: Sistema de Vendas Automatizado", 
            value="🛒 Sistema de Vendas Automatizado",
            max_length=100
        ))
        self.add_item(ui.InputText(
            label="Produto", 
            placeholder="Ex: Produtos Digitais", 
            value="Produtos Digitais",
            max_length=100
        ))
        self.add_item(ui.InputText(
            label="Descrição", 
            placeholder="Ex: Clique no botão abaixo para criar um ticket de compra", 
            value="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            style=discord.InputTextStyle.long,
            max_length=1000
        ))
        self.add_item(ui.InputText(
            label="Nome do Botão", 
            placeholder="Ex: Criar Ticket de Compra", 
            value="Criar Ticket de Compra",
            max_length=80
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a configuração do sistema de tickets"""
        try:
            headline = self.children[0].value
            produto = self.children[1].value
            descricao = self.children[2].value
            nome_botao = self.children[3].value
            
            # Criar embed com as configurações
            embed = discord.Embed(
                title=headline,
                description=descricao,
                color=0x0099ff
            )
            embed.add_field(
                name="🚀 Como Funciona?",
                value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
                inline=False
            )
            embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")
            
            # Criar view com botão personalizado
            view = TicketView(nome_botao)
            
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Erro ao configurar sistema de tickets: {e}")
            await interaction.response.send_message("❌ Erro ao configurar sistema de tickets.", ephemeral=True)

class TicketModal(ui.Modal):
    """Modal para usuário escolher produto ao criar ticket"""
    
    def __init__(self, products: List[Dict]):
        super().__init__(title="Criar Ticket de Compra", timeout=300)
        self.products = products
        self.product_model = ProductModel()
        
        # Criar select menu com produtos
        self.product_select = ui.Select(
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
        self.add_item(self.product_select)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa a criação do ticket quando o modal é submetido"""
        try:
            selected_product_id = int(self.product_select.values[0])
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
            print(f"Erro ao processar modal de ticket: {e}")
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
            # Verificar se usuário já tem ticket ativo
            from bot import active_tickets
            if interaction.user.id in active_tickets:
                await interaction.response.send_message(
                    "❌ Você já possui um ticket ativo. Use o canal do seu ticket para continuar.",
                    ephemeral=True
                )
                return
            
            # Carregar produtos disponíveis
            products = await self.product_model.get_all_products()
            
            if not products:
                await interaction.response.send_message(
                    "❌ Nenhum produto disponível no momento.",
                    ephemeral=True
                )
                return
            
            # Criar e enviar modal
            modal = TicketModal(products)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            print(f"Erro no callback do botão de ticket: {e}")
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
