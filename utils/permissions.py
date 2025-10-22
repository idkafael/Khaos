import discord
from discord.ext import commands
from discord import Interaction
from typing import Callable
from models.guild_config_model import GuildConfigModel

async def is_server_admin(interaction: Interaction) -> bool:
    """
    Verifica se o usuário tem permissão de admin no servidor
    
    Critérios:
    1. Tem permissão de Administrator no Discord
    2. OU tem uma das roles admin configuradas no servidor
    
    Args:
        interaction: Interação do Discord
    
    Returns:
        True se é admin
    """
    # Verificar permissão de administrator do Discord
    if interaction.user.guild_permissions.administrator:
        return True
    
    # Verificar roles admin configuradas
    guild_config_model = GuildConfigModel()
    admin_role_ids = await guild_config_model.get_admin_role_ids(interaction.guild_id)
    
    if admin_role_ids:
        user_role_ids = [r.id for r in interaction.user.roles]
        return any(role_id in admin_role_ids for role_id in user_role_ids)
    
    return False

def require_server_admin():
    """
    Decorator para comandos que requerem permissão de admin do servidor
    
    Usage:
        @bot.tree.command()
        @require_server_admin()
        async def meu_comando_admin(interaction):
            ...
    """
    async def predicate(interaction: Interaction) -> bool:
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ Este comando só pode ser usado em servidores!",
                ephemeral=True
            )
            return False
        
        if await is_server_admin(interaction):
            return True
        
        await interaction.response.send_message(
            "❌ Você não tem permissão para usar este comando!\n"
            "💡 Apenas administradores ou roles admin configuradas podem usar.",
            ephemeral=True
        )
        return False
    
    return commands.check(predicate)

def require_guild():
    """
    Decorator para comandos que só funcionam em servidores (não em DM)
    
    Usage:
        @bot.tree.command()
        @require_guild()
        async def meu_comando(interaction):
            ...
    """
    async def predicate(interaction: Interaction) -> bool:
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ Este comando só pode ser usado em servidores!",
                ephemeral=True
            )
            return False
        return True
    
    return commands.check(predicate)

async def check_guild_active(guild_id: int) -> bool:
    """
    Verifica se um servidor está ativo
    
    Args:
        guild_id: ID do servidor
    
    Returns:
        True se ativo
    """
    guild_config_model = GuildConfigModel()
    return await guild_config_model.is_active(guild_id)

