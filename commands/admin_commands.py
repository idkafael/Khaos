import discord
from discord import ui
from discord.ext import commands
from models.product_model import ProductModel
from models.inventory_model import InventoryModel
from typing import List

class AddStockModal(ui.Modal):
    """Modal para adicionar estoque"""
    
    def __init__(self, product_id: int, product_name: str):
        super().__init__(title=f"Adicionar Estoque: {product_name}")
        self.product_id = product_id
        self.product_name = product_name
        
        self.stock_input = ui.InputText(
            label="Códigos/Keys (um por linha)",
            style=discord.InputTextStyle.paragraph,
            placeholder="KEY-123-ABC\nKEY-456-DEF\nKEY-789-GHI",
            required=True,
            max_length=4000
        )
        self.add_item(self.stock_input)
    
    async def callback(self, interaction: discord.Interaction):
        """Processa o envio do modal"""
        try:
            # Processar linhas
            lines = self.stock_input.value.strip().split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                await interaction.response.send_message("❌ Nenhum código válido foi fornecido.", ephemeral=True)
                return
            
            # Adicionar ao estoque
            inventory_model = InventoryModel()
            added = await inventory_model.add_bulk_stock(self.product_id, lines)
            
            if added > 0:
                embed = discord.Embed(
                    title="✅ Estoque Adicionado",
                    description=f"**{added}** itens foram adicionados ao produto **{self.product_name}**.",
                    color=0x00ff00
                )
                embed.add_field(
                    name="📦 Produto",
                    value=self.product_name,
                    inline=True
                )
                embed.add_field(
                    name="➕ Itens Adicionados",
                    value=str(added),
                    inline=True
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Erro ao adicionar estoque. Verifique os logs.", ephemeral=True)
                
        except Exception as e:
            print(f"Erro ao processar adição de estoque: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)


class ProductSelect(ui.Select):
    """Select menu para escolher produto"""
    
    def __init__(self, products: List[dict], action: str = "add"):
        self.action = action
        self.products_dict = {str(p['id']): p for p in products}
        
        options = [
            discord.SelectOption(
                label=p['name'][:100],
                description=f"Categoria: {p.get('category', 'N/A')} | R$ {p['price']:.2f}"[:100],
                value=str(p['id']),
                emoji="📦"
            )
            for p in products[:25]  # Discord limit
        ]
        
        super().__init__(
            placeholder="Escolha um produto...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback quando produto é selecionado"""
        try:
            product_id = int(self.values[0])
            product = self.products_dict[str(product_id)]
            
            if self.action == "add":
                # Abrir modal para adicionar estoque
                modal = AddStockModal(product_id, product['name'])
                await interaction.response.send_modal(modal)
            elif self.action == "view":
                # Mostrar detalhes do estoque
                inventory_model = InventoryModel()
                counts = await inventory_model.get_stock_count(product_id)
                
                embed = discord.Embed(
                    title=f"📊 Estoque: {product['name']}",
                    description=f"Detalhes do estoque do produto",
                    color=0x3498db
                )
                embed.add_field(
                    name="✅ Disponível",
                    value=str(counts['available']),
                    inline=True
                )
                embed.add_field(
                    name="🔒 Reservado",
                    value=str(counts['reserved']),
                    inline=True
                )
                embed.add_field(
                    name="💰 Vendido",
                    value=str(counts['sold']),
                    inline=True
                )
                embed.add_field(
                    name="📦 Total",
                    value=str(counts['total']),
                    inline=True
                )
                embed.add_field(
                    name="💵 Valor Unitário",
                    value=f"R$ {product['price']:.2f}",
                    inline=True
                )
                embed.add_field(
                    name="💎 Valor em Estoque",
                    value=f"R$ {counts['available'] * product['price']:.2f}",
                    inline=True
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            print(f"Erro no callback do select: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)


class ProductSelectView(ui.View):
    """View com select menu de produtos"""
    
    def __init__(self, products: List[dict], action: str = "add"):
        super().__init__(timeout=300)
        self.add_item(ProductSelect(products, action))


async def setup_admin_commands(bot: discord.Bot):
    """Configura os comandos de admin"""
    
    @bot.tree.command(
        name="adicionar_estoque",
        description="[ADMIN] Adicionar itens ao estoque de um produto"
    )
    @discord.app_commands.default_permissions(administrator=True)
    async def add_stock_command(interaction: discord.Interaction):
        """Comando para adicionar estoque"""
        try:
            # Buscar todos os produtos
            product_model = ProductModel()
            products = await product_model.get_all_products()
            
            if not products:
                await interaction.response.send_message("❌ Nenhum produto cadastrado.", ephemeral=True)
                return
            
            # Criar embed de introdução
            embed = discord.Embed(
                title="➕ Adicionar Estoque",
                description="Selecione o produto para adicionar itens ao estoque.",
                color=0x3498db
            )
            embed.add_field(
                name="📝 Como funciona",
                value="1. Selecione o produto\n2. Cole os códigos/keys (um por linha)\n3. Confirme",
                inline=False
            )
            
            # Enviar com select menu
            view = ProductSelectView(products, action="add")
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Erro no comando adicionar_estoque: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)
    
    @bot.tree.command(
        name="ver_estoque",
        description="[ADMIN] Ver resumo do estoque de produtos"
    )
    @discord.app_commands.default_permissions(administrator=True)
    async def view_stock_command(interaction: discord.Interaction):
        """Comando para ver estoque"""
        try:
            inventory_model = InventoryModel()
            summary = await inventory_model.get_all_stock_summary()
            
            if not summary:
                await interaction.response.send_message("❌ Nenhum produto com estoque.", ephemeral=True)
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
            
            # Adicionar botão para ver detalhes
            product_model = ProductModel()
            products = await product_model.get_all_products()
            view = ProductSelectView(products, action="view")
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Erro no comando ver_estoque: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)
    
    print("✅ Comandos de admin configurados")

