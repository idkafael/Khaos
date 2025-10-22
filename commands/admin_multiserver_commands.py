"""
Comandos Admin para Sistema Multi-Servidor
Integre estes comandos no bot.py
"""

import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import require_server_admin, require_guild
from models.product_model import ProductModel
from models.guild_config_model import GuildConfigModel
from typing import Optional

# ===============================
# COMANDOS DE PRODUTOS
# ===============================

@app_commands.command(name="admin_criar_produto", description="[ADMIN] Criar um produto no servidor")
@app_commands.describe(
    nome="Nome do produto",
    preco="Preço em R$",
    descricao="Descrição do produto",
    categoria="Categoria (deixe vazio para produto normal)"
)
async def admin_criar_produto_cmd(
    interaction: discord.Interaction,
    nome: str,
    preco: float,
    descricao: str,
    categoria: Optional[str] = "produto"
):
    """Criar produto (integrar no bot.py com @require_server_admin())"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        product_model = ProductModel()
        
        product_data = {
            'name': nome,
            'price': preco,
            'description': descricao,
            'category': categoria
        }
        
        product = await product_model.create_product(interaction.guild_id, product_data)
        
        if product:
            embed = discord.Embed(
                title="✅ Produto Criado",
                description=f"Produto **{nome}** criado com sucesso!",
                color=discord.Color.green()
            )
            embed.add_field(name="ID", value=product['id'], inline=True)
            embed.add_field(name="Preço", value=f"R$ {preco:.2f}", inline=True)
            embed.add_field(name="Categoria", value=categoria, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Erro ao criar produto.", ephemeral=True)
            
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)


@app_commands.command(name="admin_criar_vip", description="[ADMIN] Criar produto VIP no servidor")
@app_commands.describe(
    nome="Nome do produto VIP (ex: VIP Gold - 30 Dias)",
    preco="Preço em R$",
    role_name="Nome da role Discord (ex: VIP Gold)",
    duracao_dias="Duração em dias (deixe vazio para vitalício)",
    descricao="Descrição do produto VIP"
)
async def admin_criar_vip_cmd(
    interaction: discord.Interaction,
    nome: str,
    preco: float,
    role_name: str,
    descricao: str,
    duracao_dias: Optional[int] = None
):
    """Criar produto VIP (integrar no bot.py com @require_server_admin())"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        product_model = ProductModel()
        
        # Configuração VIP
        vip_config = {
            "role_name": role_name,
            "duration_days": duracao_dias
        }
        
        product_data = {
            'name': nome,
            'price': preco,
            'description': descricao,
            'category': 'vip',
            'vip_config': vip_config
        }
        
        product = await product_model.create_product(interaction.guild_id, product_data)
        
        if product:
            duracao_text = f"{duracao_dias} dias" if duracao_dias else "Vitalício"
            
            embed = discord.Embed(
                title="✅ Produto VIP Criado",
                description=f"VIP **{nome}** criado com sucesso!",
                color=discord.Color.gold()
            )
            embed.add_field(name="ID", value=product['id'], inline=True)
            embed.add_field(name="Preço", value=f"R$ {preco:.2f}", inline=True)
            embed.add_field(name="Role", value=role_name, inline=True)
            embed.add_field(name="Duração", value=duracao_text, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Erro ao criar produto VIP.", ephemeral=True)
            
    except Exception as e:
        print(f"Erro ao criar VIP: {e}")
        await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)


@app_commands.command(name="admin_listar_produtos", description="[ADMIN] Listar todos os produtos do servidor")
async def admin_listar_produtos_cmd(interaction: discord.Interaction):
    """Listar produtos do servidor (integrar no bot.py com @require_server_admin())"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        product_model = ProductModel()
        products = await product_model.get_products_by_guild(interaction.guild_id)
        
        if not products:
            await interaction.followup.send("📦 Nenhum produto cadastrado neste servidor.", ephemeral=True)
            return
        
        # Separar por categoria
        vips = [p for p in products if p.get('category') == 'vip']
        normais = [p for p in products if p.get('category') != 'vip']
        
        embed = discord.Embed(
            title=f"📦 Produtos do Servidor ({len(products)} total)",
            color=discord.Color.blue()
        )
        
        if normais:
            produtos_text = "\n".join([
                f"**#{p['id']}** - {p['name']} - R$ {p['price']:.2f}"
                for p in normais[:10]
            ])
            embed.add_field(
                name=f"🛍️ Produtos Normais ({len(normais)})",
                value=produtos_text or "Nenhum",
                inline=False
            )
        
        if vips:
            vips_text = "\n".join([
                f"**#{p['id']}** - {p['name']} - R$ {p['price']:.2f}"
                for p in vips[:10]
            ])
            embed.add_field(
                name=f"👑 Produtos VIP ({len(vips)})",
                value=vips_text or "Nenhum",
                inline=False
            )
        
        if len(products) > 20:
            embed.set_footer(text=f"Mostrando 20 de {len(products)} produtos")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)


@app_commands.command(name="admin_deletar_produto", description="[ADMIN] Deletar um produto do servidor")
@app_commands.describe(product_id="ID do produto a deletar")
async def admin_deletar_produto_cmd(interaction: discord.Interaction, product_id: int):
    """Deletar produto (integrar no bot.py com @require_server_admin())"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        product_model = ProductModel()
        
        # Buscar produto para confirmar que existe e pertence ao servidor
        product = await product_model.get_product_by_id(product_id, interaction.guild_id)
        
        if not product:
            await interaction.followup.send("❌ Produto não encontrado neste servidor.", ephemeral=True)
            return
        
        # Deletar
        success = await product_model.delete_product(product_id, interaction.guild_id)
        
        if success:
            embed = discord.Embed(
                title="✅ Produto Deletado",
                description=f"Produto **{product['name']}** deletado com sucesso!",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Erro ao deletar produto.", ephemeral=True)
            
    except Exception as e:
        print(f"Erro ao deletar produto: {e}")
        await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)


# ===============================
# COMANDO DE CONFIGURAÇÃO
# ===============================

@app_commands.command(name="admin_configurar", description="[ADMIN] Configurar o servidor")
async def admin_configurar_cmd(interaction: discord.Interaction):
    """Configurar servidor (integrar no bot.py com @require_server_admin())"""
    try:
        # Este comando abre um modal para configuração
        # Por simplicidade, vou criar uma versão básica
        
        await interaction.response.defer(ephemeral=True)
        
        guild_config_model = GuildConfigModel()
        config = await guild_config_model.get_config(interaction.guild_id)
        
        if config:
            embed = discord.Embed(
                title="⚙️ Configuração Atual do Servidor",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Nome",
                value=config.get('guild_name', 'Não configurado'),
                inline=False
            )
            
            embed.add_field(
                name="PushinPay API Key",
                value="Configurada" if config.get('pushinpay_api_key') else "Usando global",
                inline=True
            )
            
            split_percent = config.get('pushinpay_split_percent', 0)
            embed.add_field(
                name="Split de Pagamento",
                value=f"{split_percent}%" if split_percent > 0 else "Não configurado",
                inline=True
            )
            
            embed.add_field(
                name="Status",
                value="✅ Ativo" if config.get('is_active', True) else "❌ Inativo",
                inline=True
            )
            
            embed.set_footer(text="Use os comandos específicos para alterar cada configuração")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            # Criar configuração básica
            await guild_config_model.create_or_update_config(
                guild_id=interaction.guild_id,
                guild_name=interaction.guild.name,
                is_active=True
            )
            
            await interaction.followup.send(
                "✅ Configuração inicial criada! Use `/admin_configurar` novamente para ver.",
                ephemeral=True
            )
            
    except Exception as e:
        print(f"Erro ao configurar: {e}")
        await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)


# ===============================
# INSTRUÇÕES DE INTEGRAÇÃO
# ===============================

"""
COMO INTEGRAR NO bot.py:

1. No início do bot.py, importar:

from utils.permissions import require_server_admin
from models.product_model import ProductModel
from models.guild_config_model import GuildConfigModel

2. Para cada comando acima, adicionar no bot.py:

@bot.tree.command(name="admin_criar_produto", description="[ADMIN] Criar um produto no servidor")
@require_server_admin()
async def admin_criar_produto(interaction, nome, preco, descricao, categoria=None):
    # Copiar o código da função admin_criar_produto_cmd acima
    pass

3. Fazer o mesmo para todos os comandos:
   - admin_criar_produto
   - admin_criar_vip
   - admin_listar_produtos
   - admin_deletar_produto
   - admin_configurar

4. Sincronizar comandos no bot startup:
   await bot.tree.sync()
"""

