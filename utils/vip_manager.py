import disnake
from disnake import Role, Member, Guild
from models.vip_model import VipModel
from typing import Optional, Dict
from datetime import datetime, timedelta

class VipManager:
    """Gerenciador de roles VIP e notificações"""
    
    def __init__(self, bot):
        self.bot = bot
        self.vip_model = VipModel()
        
        # Configurações de cores para cada role VIP
        self.role_colors = {
            'KHAOS': disnake.Color.from_rgb(138, 43, 226),          # Roxo (Blue Violet)
            'VIP Bronze': disnake.Color.from_rgb(205, 127, 50),    # Bronze
            'VIP Prata': disnake.Color.from_rgb(192, 192, 192),     # Prata
            'VIP Ouro': disnake.Color.from_rgb(255, 215, 0),        # Ouro
            'VIP Platina': disnake.Color.from_rgb(229, 228, 226),   # Platina
            'VIP Diamante': disnake.Color.from_rgb(185, 242, 255),  # Diamante
        }
    
    async def grant_vip_role(
        self,
        member: Member,
        role_name: str,
        create_if_not_exists: bool = True
    ) -> Optional[Role]:
        """
        Adiciona uma role VIP a um membro
        
        Args:
            member: Membro do Discord
            role_name: Nome da role VIP
            create_if_not_exists: Se True, cria a role se não existir
        
        Returns:
            Role adicionada ou None em caso de erro
        """
        try:
            guild = member.guild
            
            # Buscar role existente
            role = disnake.utils.get(guild.roles, name=role_name)
            
            # Criar role se não existir
            if not role and create_if_not_exists:
                role = await self._create_vip_role(guild, role_name)
                if not role:
                    print(f"❌ Erro ao criar role {role_name}")
                    return None
            
            if not role:
                print(f"❌ Role {role_name} não encontrada e criação desabilitada")
                return None
            
            # Adicionar role ao membro
            await member.add_roles(role, reason="Assinatura VIP adquirida")
            print(f"✅ Role {role_name} adicionada a {member.name}")
            
            return role
            
        except discord.Forbidden:
            print(f"❌ Sem permissão para adicionar role a {member.name}")
            return None
        except Exception as e:
            print(f"❌ Erro ao adicionar role VIP: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def remove_vip_role(self, subscription: Dict) -> bool:
        """
        Remove uma role VIP de um membro
        
        Args:
            subscription: Dados da assinatura VIP
        
        Returns:
            True se removeu com sucesso
        """
        try:
            guild = self.bot.get_guild(subscription['guild_id'])
            if not guild:
                print(f"❌ Servidor {subscription['guild_id']} não encontrado")
                return False
            
            member = guild.get_member(subscription['user_id'])
            if not member:
                print(f"⚠️ Usuário {subscription['user_id']} não está mais no servidor")
                return False
            
            role = guild.get_role(subscription['role_id'])
            if not role:
                print(f"⚠️ Role {subscription['role_id']} não encontrada")
                return False
            
            await member.remove_roles(role, reason="Assinatura VIP expirada")
            print(f"🔻 Role {role.name} removida de {member.name}")
            
            return True
            
        except discord.Forbidden:
            print(f"❌ Sem permissão para remover role")
            return False
        except Exception as e:
            print(f"❌ Erro ao remover role VIP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_vip_welcome_dm(self, member: Member, subscription: Dict, product: Dict) -> bool:
        """
        Envia DM de boas-vindas ao novo VIP
        
        Args:
            member: Membro do Discord
            subscription: Dados da assinatura
            product: Dados do produto VIP
        
        Returns:
            True se enviou com sucesso
        """
        try:
            embed = discord.Embed(
                title="🎉 Bem-vindo ao VIP!",
                description=f"Parabéns {member.mention}! Sua assinatura VIP foi ativada com sucesso.",
                color=disnake.Color.gold(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👑 Role VIP",
                value=f"**{subscription['role_name']}**",
                inline=True
            )
            
            # Informações de duração
            if subscription['duration_days'] is None:
                duration_text = "🌟 **VITALÍCIO** - Seu VIP nunca expira!"
            else:
                expires_at = datetime.fromisoformat(subscription['expires_at'].replace('Z', '+00:00'))
                duration_text = f"⏰ **{subscription['duration_days']} dias**\nExpira em: <t:{int(expires_at.timestamp())}:F>"
            
            embed.add_field(
                name="📅 Duração",
                value=duration_text,
                inline=True
            )
            
            embed.add_field(
                name="✨ Benefícios",
                value="• Acesso a canais exclusivos VIP\n"
                      "• Prioridade no suporte\n"
                      "• Descontos especiais\n"
                      "• Conteúdo exclusivo",
                inline=False
            )
            
            if subscription['duration_days'] is not None:
                embed.add_field(
                    name="🔄 Renovação",
                    value="Use `/renovar_vip` para renovar sua assinatura antes do vencimento.",
                    inline=False
                )
            
            embed.set_footer(
                text=f"Compra #{subscription['transaction_id']} • {member.guild.name}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            await member.send(embed=embed)
            print(f"📬 DM de boas-vindas VIP enviada para {member.name}")
            
            return True
            
        except discord.Forbidden:
            print(f"⚠️ {member.name} está com DMs desabilitadas")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar DM de boas-vindas: {e}")
            return False
    
    async def send_vip_expiration_warning(self, subscription: Dict) -> bool:
        """
        Envia aviso de que o VIP está próximo de expirar
        
        Args:
            subscription: Dados da assinatura
        
        Returns:
            True se enviou com sucesso
        """
        try:
            guild = self.bot.get_guild(subscription['guild_id'])
            if not guild:
                return False
            
            member = guild.get_member(subscription['user_id'])
            if not member:
                return False
            
            # Calcular dias restantes
            expires_at = datetime.fromisoformat(subscription['expires_at'].replace('Z', '+00:00'))
            days_left = (expires_at.replace(tzinfo=None) - datetime.now()).days
            
            embed = discord.Embed(
                title="⚠️ Seu VIP está próximo de expirar!",
                description=f"Olá {member.mention}! Sua assinatura VIP **{subscription['role_name']}** está próxima do vencimento.",
                color=disnake.Color.orange(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📅 Expira em",
                value=f"**{days_left} dia(s)**\n<t:{int(expires_at.timestamp())}:F>",
                inline=False
            )
            
            embed.add_field(
                name="🔄 Como Renovar",
                value="Para continuar aproveitando os benefícios VIP:\n"
                      "1. Use o comando `/renovar_vip` no servidor\n"
                      "2. Escolha o plano desejado\n"
                      "3. Complete o pagamento",
                inline=False
            )
            
            embed.add_field(
                name="💡 Dica",
                value="Renove antes do vencimento para não perder o acesso aos canais VIP!",
                inline=False
            )
            
            embed.set_footer(
                text=f"{guild.name}",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            await member.send(embed=embed)
            print(f"⚠️ Aviso de expiração enviado para {member.name} ({days_left} dias restantes)")
            
            return True
            
        except discord.Forbidden:
            print(f"⚠️ Não foi possível enviar aviso de expiração (DMs desabilitadas)")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar aviso de expiração: {e}")
            return False
    
    async def send_vip_expired_dm(self, subscription: Dict) -> bool:
        """
        Envia notificação de que o VIP expirou
        
        Args:
            subscription: Dados da assinatura expirada
        
        Returns:
            True se enviou com sucesso
        """
        try:
            guild = self.bot.get_guild(subscription['guild_id'])
            if not guild:
                return False
            
            member = guild.get_member(subscription['user_id'])
            if not member:
                return False
            
            embed = discord.Embed(
                title="⏰ Seu VIP Expirou",
                description=f"Olá {member.mention}! Sua assinatura VIP **{subscription['role_name']}** expirou.",
                color=disnake.Color.red(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📅 Data de Expiração",
                value=f"<t:{int(datetime.fromisoformat(subscription['expires_at'].replace('Z', '+00:00')).timestamp())}:F>",
                inline=False
            )
            
            embed.add_field(
                name="🔄 Renovar Assinatura",
                value="Sentiremos sua falta! Para voltar a ter acesso VIP:\n"
                      "1. Use o comando `/renovar_vip` no servidor\n"
                      "2. Escolha o plano que mais combina com você\n"
                      "3. Complete o pagamento e volte ao VIP!",
                inline=False
            )
            
            embed.add_field(
                name="💎 Benefícios VIP",
                value="Lembre-se: Como VIP você tem acesso a:\n"
                      "• Canais exclusivos\n"
                      "• Prioridade no suporte\n"
                      "• Descontos especiais\n"
                      "• E muito mais!",
                inline=False
            )
            
            embed.set_footer(
                text=f"Esperamos você de volta! • {guild.name}",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            await member.send(embed=embed)
            print(f"⏰ Notificação de expiração enviada para {member.name}")
            
            return True
            
        except discord.Forbidden:
            print(f"⚠️ Não foi possível enviar notificação de expiração (DMs desabilitadas)")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar notificação de expiração: {e}")
            return False
    
    async def process_vip_purchase(
        self,
        member: Member,
        product: Dict,
        transaction_id: int
    ) -> Optional[Dict]:
        """
        Processa a compra de um produto VIP
        
        Args:
            member: Membro que comprou
            product: Dados do produto VIP
            transaction_id: ID da transação
        
        Returns:
            Dados da assinatura criada ou None
        """
        try:
            # Extrair configuração VIP do produto
            vip_config = product.get('vip_config', {})
            
            if not vip_config:
                print(f"⚠️ Produto {product['name']} não tem configuração VIP")
                return None
            
            role_name = vip_config.get('role_name', 'VIP')
            duration_days = vip_config.get('duration_days')
            
            # Adicionar role ao membro
            role = await self.grant_vip_role(member, role_name)
            if not role:
                print(f"❌ Falha ao adicionar role VIP a {member.name}")
                return None
            
            # Criar assinatura no banco de dados
            subscription = await self.vip_model.create_subscription(
                user_id=member.id,
                guild_id=member.guild.id,
                role_id=role.id,
                role_name=role_name,
                product_id=product['id'],
                duration_days=duration_days,
                transaction_id=transaction_id
            )
            
            if not subscription:
                print(f"❌ Falha ao criar assinatura VIP para {member.name}")
                # Tentar remover a role se falhou
                await member.remove_roles(role, reason="Falha ao criar assinatura")
                return None
            
            # Enviar DM de boas-vindas
            await self.send_vip_welcome_dm(member, subscription, product)
            
            print(f"🎉 VIP processado com sucesso para {member.name} - {role_name}")
            
            return subscription
            
        except Exception as e:
            print(f"❌ Erro ao processar compra VIP: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def renew_vip(self, member: Member, product: Dict, transaction_id: int) -> Optional[Dict]:
        """
        Renova uma assinatura VIP existente
        
        Args:
            member: Membro que está renovando
            product: Dados do produto VIP
            transaction_id: ID da transação
        
        Returns:
            Dados da nova assinatura ou None
        """
        try:
            # Buscar assinatura atual
            current_sub = await self.vip_model.get_user_subscription(
                member.id,
                member.guild.id
            )
            
            # Se tem assinatura ativa, cancelar
            if current_sub:
                await self.vip_model.cancel_subscription(current_sub['id'])
                print(f"🔄 Assinatura anterior cancelada para renovação")
            
            # Criar nova assinatura (funciona igual a uma compra nova)
            return await self.process_vip_purchase(member, product, transaction_id)
            
        except Exception as e:
            print(f"❌ Erro ao renovar VIP: {e}")
            return None
    
    async def _create_vip_role(self, guild: Guild, role_name: str) -> Optional[Role]:
        """
        Cria uma role VIP no servidor
        
        Args:
            guild: Servidor Discord
            role_name: Nome da role a criar
        
        Returns:
            Role criada ou None em caso de erro
        """
        try:
            # Obter cor para a role
            color = self.role_colors.get(role_name, disnake.Color.purple())
            
            # Criar role
            role = await guild.create_role(
                name=role_name,
                color=color,
                hoist=True,  # Mostrar separadamente na lista de membros
                mentionable=True,
                reason="Role VIP criada automaticamente pelo bot"
            )
            
            print(f"✅ Role {role_name} criada no servidor {guild.name}")
            
            return role
            
        except discord.Forbidden:
            print(f"❌ Sem permissão para criar role no servidor {guild.name}")
            return None
        except Exception as e:
            print(f"❌ Erro ao criar role VIP: {e}")
            return None


