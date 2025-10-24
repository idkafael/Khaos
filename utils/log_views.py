import discord
from discord import ui
from models.guild_config_model import GuildConfigModel

# Todos os eventos disponíveis para log
LOG_EVENTS = {
    # Vendas (🔥 Mais usado)
    'payment_confirmed': {'emoji': '✅', 'name': 'Pagamentos Confirmados', 'category': '💰 Vendas'},
    'product_delivered': {'emoji': '📦', 'name': 'Produtos Entregues', 'category': '💰 Vendas'},
    'payment_generated': {'emoji': '💳', 'name': 'Pagamentos Gerados', 'category': '💰 Vendas'},
    
    # Tickets
    'ticket_created': {'emoji': '🎫', 'name': 'Tickets de Compra Criados', 'category': '🎫 Tickets'},
    'support_ticket_created': {'emoji': '🆘', 'name': 'Tickets de Suporte Criados', 'category': '🎫 Tickets'},
    'ticket_closed': {'emoji': '🔒', 'name': 'Tickets Fechados', 'category': '🎫 Tickets'},
    
    # Extras
    'coupon_used': {'emoji': '🎟️', 'name': 'Cupons Utilizados', 'category': '🎁 Extras'},
    'vip_activated': {'emoji': '👑', 'name': 'VIP Ativado', 'category': '🎁 Extras'},
    'vip_expired': {'emoji': '⏰', 'name': 'VIP Expirado', 'category': '🎁 Extras'},
    'stock_added': {'emoji': '📦', 'name': 'Estoque Adicionado', 'category': '🎁 Extras'},
    'product_created': {'emoji': '➕', 'name': 'Produtos Criados', 'category': '🎁 Extras'}
}

class LogEventsSelect(ui.Select):
    """Select menu para escolher eventos de log"""
    
    def __init__(self, log_channel_id: int, guild_id: int):
        self.log_channel_id = log_channel_id
        self.guild_id = guild_id
        
        # Criar opções do select
        options = []
        for event_id, event_data in LOG_EVENTS.items():
            options.append(discord.SelectOption(
                label=event_data['name'],
                value=event_id,
                emoji=event_data['emoji'],
                description=event_data['category']
            ))
        
        super().__init__(
            placeholder="Escolha os eventos para logar (múltipla escolha)...",
            min_values=0,  # Pode não selecionar nada (desabilita logs)
            max_values=len(options),  # Pode selecionar todos
            options=options,
            custom_id="log_events_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback quando eventos são selecionados"""
        try:
            selected_events = self.values  # Lista de event_ids selecionados
            
            # Salvar configuração
            guild_config = GuildConfigModel()
            
            if not selected_events:
                # Desabilitar logs
                success = await guild_config.disable_logs(self.guild_id)
                
                if success:
                    embed = discord.Embed(
                        title="❌ Logs Desabilitados",
                        description="O sistema de logs foi desabilitado para este servidor.",
                        color=0xFF0000
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(
                        "❌ Erro ao desabilitar logs.",
                        ephemeral=True
                    )
                return
            
            # Salvar eventos selecionados
            success = await guild_config.set_log_config(
                guild_id=self.guild_id,
                log_channel_id=self.log_channel_id,
                log_events=selected_events
            )
            
            if success:
                # Criar resumo dos eventos selecionados
                events_list = []
                for event_id in selected_events:
                    event_data = LOG_EVENTS.get(event_id, {})
                    emoji = event_data.get('emoji', '📋')
                    name = event_data.get('name', event_id)
                    events_list.append(f"{emoji} {name}")
                
                embed = discord.Embed(
                    title="✅ Logs Configurados!",
                    description=f"Sistema de logs ativado com sucesso!\n"
                                f"📺 **Canal:** <#{self.log_channel_id}>",
                    color=0x00FF00
                )
                
                embed.add_field(
                    name=f"📊 Eventos Selecionados ({len(selected_events)})",
                    value="\n".join(events_list),
                    inline=False
                )
                
                embed.add_field(
                    name="💡 Dica",
                    value="Use `/setlog` novamente para modificar os eventos.",
                    inline=False
                )
                
                embed.set_footer(text="Os logs começarão a ser enviados imediatamente!")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                # Enviar mensagem de teste no canal de logs
                try:
                    log_channel = interaction.guild.get_channel(self.log_channel_id)
                    if log_channel:
                        test_embed = discord.Embed(
                            title="🎉 Sistema de Logs Ativado!",
                            description=f"Logs configurados por {interaction.user.mention}",
                            color=0x5865F2
                        )
                        test_embed.add_field(
                            name="📊 Eventos Ativos",
                            value=f"{len(selected_events)} eventos selecionados",
                            inline=True
                        )
                        test_embed.set_footer(text="Este é um teste - os logs reais começam agora!")
                        await log_channel.send(embed=test_embed)
                except:
                    pass  # Ignorar erro ao enviar mensagem de teste
                
            else:
                await interaction.response.send_message(
                    "❌ Erro ao salvar configuração de logs.",
                    ephemeral=True
                )
                
        except Exception as e:
            print(f"Erro ao salvar configuração de logs: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Erro ao processar seleção de eventos.",
                ephemeral=True
            )

class PresetButton(ui.Button):
    """Botão para aplicar um preset de eventos"""
    
    def __init__(self, label: str, emoji: str, events: list, row: int = 1):
        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
            row=row
        )
        self.events = events
    
    async def callback(self, interaction: discord.Interaction):
        """Aplicar preset"""
        # Atualizar o select com os eventos do preset
        view = self.view
        select = view.children[0]  # O select é o primeiro item
        select.values = self.events
        
        # Trigger o callback do select
        await select.callback(interaction)

class LogEventsSelectView(ui.View):
    """View com select menu e botões de preset"""
    
    def __init__(self, log_channel_id: int, guild_id: int):
        super().__init__(timeout=300)  # 5 minutos
        
        # Adicionar select menu
        self.add_item(LogEventsSelect(log_channel_id, guild_id))
        
        # Adicionar botões de preset
        self.add_item(PresetButton(
            label="Apenas Vendas",
            emoji="🔥",
            events=['payment_confirmed', 'product_delivered'],
            row=1
        ))
        
        self.add_item(PresetButton(
            label="Todos Tickets",
            emoji="🎫",
            events=['ticket_created', 'support_ticket_created', 'ticket_closed'],
            row=1
        ))
        
        self.add_item(PresetButton(
            label="Completo",
            emoji="📊",
            events=list(LOG_EVENTS.keys()),
            row=1
        ))
        
        # Botão para limpar/desabilitar
        self.add_item(PresetButton(
            label="Desabilitar Logs",
            emoji="❌",
            events=[],
            row=1
        ))
    
    async def on_timeout(self):
        """Quando o timeout expira"""
        for item in self.children:
            item.disabled = True

