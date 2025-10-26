import discord
from discord import ui
from discord.ext import commands
from models.product_model import ProductModel
from models.inventory_model import InventoryModel
from typing import List

class AddStockModal(ui.Modal):
    """Modal para adicionar estoque"""
    
    # InputText como atributo de classe
    stock_input = ui.InputText(
        label="Códigos/Keys (um por linha)",
        style=discord.InputTextStyle.paragraph,
        placeholder="KEY-123-ABC\nKEY-456-DEF\nKEY-789-GHI",
        required=True,
        max_length=4000
    )
    
    def __init__(self, product_id: int, product_name: str):
        # SEM timeout, SEM custom_id
        super().__init__(title=f"Adicionar Estoque: {product_name}")
        self.product_id = product_id
        self.product_name = product_name
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa o envio do modal"""
        # Medição de performance
        import time
        start_time = time.time()
        
        # SEMPRE DEFER IMEDIATO (< 3 segundos)
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Processar linhas
            lines = self.stock_input.value.strip().split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                error_embed = discord.Embed(
                    title="❌ Erro",
                    description="Nenhum código válido foi fornecido.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            
            # Processamento pesado APÓS defer (com timeout)
            try:
                inventory_model = InventoryModel()
                
                # Timeout de 10s para operação de BD
                import asyncio
                added = await asyncio.wait_for(
                    inventory_model.add_bulk_stock(self.product_id, lines),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                error_embed = discord.Embed(
                    title="❌ Erro",
                    description="Processamento demorou muito. Tente novamente.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            except Exception as db_error:
                print(f"❌ Erro de conexão com banco: {db_error}")
                error_embed = discord.Embed(
                    title="❌ Erro de Conexão",
                    description="Erro de conexão com o banco de dados. Tente novamente em instantes.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            
            # Resposta de sucesso
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
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                error_embed = discord.Embed(
                    title="❌ Erro",
                    description="Erro ao adicionar estoque. Verifique os logs.",
                    color=0xff0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            
            # Log de performance
            elapsed = time.time() - start_time
            print(f"⏱️ Modal processado em {elapsed:.2f}s")
                
        except Exception as e:
            print(f"❌ Erro ao processar adição de estoque: {e}")
            import traceback
            traceback.print_exc()
            
            error_embed = discord.Embed(
                title="❌ Erro",
                description=f"Erro inesperado: {str(e)[:100]}",
                color=0xff0000
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        """Handler de erros do modal"""
        print(f"❌ ERRO NO MODAL AddStockModal: {error}")
        import traceback
        traceback.print_exc()
        
        error_embed = discord.Embed(
            title="❌ Erro",
            description=f"Erro inesperado: {str(error)[:100]}",
            color=0xff0000
        )
        try:
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        except:
            pass  # Ignorar se falhar


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
    # Nota: Todos os comandos slash foram movidos para bot.py para evitar duplicação
    # Este arquivo agora contém apenas modais e views para uso pelos comandos
    print("✅ Modais e views de admin carregados")

