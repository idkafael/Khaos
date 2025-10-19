import discord
from discord.ext import commands
from models.product_model import ProductModel

class ProductCommands(commands.Cog):
    """Comandos relacionados aos produtos"""
    
    def __init__(self, bot):
        self.bot = bot
        self.product_model = ProductModel()
    
    @commands.command(name='list_products')
    async def list_products(self, ctx):
        """Lista todos os produtos disponíveis"""
        try:
            products = await self.product_model.get_all_products()
            
            if not products:
                await ctx.send("❌ Nenhum produto disponível no momento.")
                return
            
            embed = discord.Embed(
                title="🛍️ Lista de Produtos",
                description="Todos os produtos disponíveis:",
                color=0x0099ff
            )
            
            for i, product in enumerate(products, 1):
                embed.add_field(
                    name=f"{i}. {product['name']}",
                    value=f"**Preço:** R$ {product['price']:.2f}\n**Categoria:** {product.get('category', 'N/A')}\n**Descrição:** {product['description'][:100]}...",
                    inline=False
                )
            
            embed.set_footer(text=f"Total: {len(products)} produtos")
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            await ctx.send("❌ Erro ao carregar lista de produtos.")
    
    @commands.command(name='product_info')
    async def product_info(self, ctx, *, product_name):
        """Exibe informações detalhadas de um produto"""
        try:
            product = await self.product_model.get_product_by_name(product_name)
            
            if not product:
                await ctx.send("❌ Produto não encontrado.")
                return
            
            embed = discord.Embed(
                title=f"🛒 {product['name']}",
                description=product['description'],
                color=0x00ff00
            )
            
            embed.add_field(
                name="💰 Preço",
                value=f"R$ {product['price']:.2f}",
                inline=True
            )
            embed.add_field(
                name="📂 Categoria",
                value=product.get('category', 'N/A'),
                inline=True
            )
            embed.add_field(
                name="🆔 ID",
                value=str(product['id']),
                inline=True
            )
            
            if product.get('created_at'):
                embed.add_field(
                    name="📅 Adicionado em",
                    value=product['created_at'].strftime("%d/%m/%Y %H:%M"),
                    inline=False
                )
            
            embed.set_footer(text="Use !buy <nome_do_produto> para comprar")
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
            await ctx.send("❌ Erro ao buscar informações do produto.")
    
    @commands.command(name='search_products')
    async def search_products(self, ctx, *, search_term):
        """Busca produtos por nome ou descrição"""
        try:
            products = await self.product_model.search_products(search_term)
            
            if not products:
                await ctx.send(f"❌ Nenhum produto encontrado para '{search_term}'.")
                return
            
            embed = discord.Embed(
                title=f"🔍 Resultados da Busca: '{search_term}'",
                description=f"Encontrados {len(products)} produto(s):",
                color=0xffa500
            )
            
            for product in products:
                embed.add_field(
                    name=f"🛒 {product['name']}",
                    value=f"**Preço:** R$ {product['price']:.2f}\n**Descrição:** {product['description'][:100]}...",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            await ctx.send("❌ Erro ao realizar busca de produtos.")

async def setup(bot):
    await bot.add_cog(ProductCommands(bot))
