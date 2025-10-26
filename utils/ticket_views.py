# disnake: Usa ui.TextInput com sintaxe superior para modais
import disnake
from disnake import ui
from typing import List, Dict, Optional
from models.product_model import ProductModel
from utils.ticket_manager import TicketManager
import asyncio
import time

# Sistema de gerenciamento de views ativas
active_config_views = {}

class RoleSelect(ui.Select):
    """Select menu para escolher cargo a mencionar"""
    
    def __init__(self, ticket_type: str, guild: disnake.Guild):
        # Buscar todos os cargos do servidor
        roles = [role for role in guild.roles if not role.is_bot_managed() and role.name != "@everyone"]
        roles.sort(key=lambda r: r.position, reverse=True)
        
        options = []
        for role in roles[:24]:  # Limite de 25 opções
            options.append(disnake.SelectOption(
                label=role.name,
                value=str(role.id),
                emoji="👤"
            ))
        
        # Adicionar opção "Nenhum cargo"
        options.insert(0, disnake.SelectOption(
            label="Nenhum cargo",
            value="none",
            description="Não mencionar nenhum cargo",
            emoji="🚫"
        ))
        
        super().__init__(
            placeholder="👤 Escolha o cargo a mencionar...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.ticket_type = ticket_type
        self.guild = guild
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback quando usuário seleciona um cargo"""
        selected_value = self.values[0]
        
        # Atualizar view pai com cargo selecionado
        self.view.selected_role = None if selected_value == "none" else int(selected_value)
        
        # Desabilitar select
        self.disabled = True
        
        # Atualizar mensagem
        role_mention = "Nenhum cargo" if selected_value == "none" else f"<@&{self.view.selected_role}>"
        embed = disnake.Embed(
            title="⚙️ Configuração de Ticket",
            description=f"**Cargo selecionado:** {role_mention}\n\n✅ Prosseguindo...",
            color=0x0099ff
        )
        await interaction.response.edit_message(embed=embed, view=self.view)
        
        # Se for tipo payment, prosseguir para seleção de produtos
        if self.ticket_type == 'payment':
            await asyncio.sleep(1)
            # Criar select de produtos
            product_select = ProductSelectionSelect(self.ticket_type, self.view.selected_role)
            role_view = ui.View(timeout=300)
            role_view.selected_role = self.view.selected_role
            role_view.add_item(product_select)
            
            embed = disnake.Embed(
                title="🛍️ Seleção de Produtos",
                description="Escolha os produtos que estarão disponíveis neste ticket:",
                color=0x0099ff
            )
            await interaction.followup.send(embed=embed, view=role_view, ephemeral=True)
        else:
            # Para outros tipos, ir direto para configuração detalhada
            await asyncio.sleep(1)
            ticket_config_view = TicketConfigView(interaction.guild_id, ticket_type=self.ticket_type, mention_role=self.view.selected_role)
            new_embed = ticket_config_view._create_embed()
            await interaction.followup.send(embed=new_embed, view=ticket_config_view, ephemeral=True)

class ProductSelectionSelect(ui.Select):
    """Select menu para escolher produtos disponíveis"""
    
    def __init__(self, ticket_type: str, mention_role: int = None):
        # Este select será populado dinamicamente com produtos do banco
        options = [
            disnake.SelectOption(
                label="Todos os produtos",
                value="all",
                description="Todos os produtos estarão disponíveis",
                emoji="✅"
            ),
            disnake.SelectOption(
                label="Selecionar produtos específicos",
                value="specific",
                description="Escolher quais produtos aparecem",
                emoji="🎯"
            )
        ]
        
        super().__init__(
            placeholder="🎯 Escolha os produtos...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.ticket_type = ticket_type
        self.mention_role = mention_role
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback quando usuário seleciona opção de produtos"""
        selected_value = self.values[0]
        
        # Desabilitar select
        self.disabled = True
        
        # Atualizar view pai
        product_ids = None if selected_value == "all" else []
        self.view.selected_product_ids = product_ids
        self.view.product_selection_mode = selected_value
        
        # Se selecionou "todos os produtos"
        if selected_value == "all":
            # Ir direto para configuração detalhada
            ticket_config_view = TicketConfigView(
                interaction.guild_id, 
                ticket_type=self.ticket_type,
                mention_role=self.mention_role,
                product_ids=None
            )
            new_embed = ticket_config_view._create_embed()
            
            embed = disnake.Embed(
                title="⚙️ Configuração",
                description="**Produtos:** Todos os produtos\n\n✅ Prosseguindo para configurações detalhadas...",
                color=0x0099ff
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
            await asyncio.sleep(1)
            await interaction.followup.send(embed=new_embed, view=ticket_config_view, ephemeral=True)
        else:
            # Abrir modal para inserir IDs dos produtos
            modal = ProductFilterModalForSetup()
            await interaction.response.send_modal(modal)
        
        # Armazenar dados no modal/view para uso posterior
        interaction.client._setup_data = {
            'ticket_type': self.ticket_type,
            'mention_role': self.mention_role
        }

class ProductFilterModalForSetup(ui.Modal):
    """Modal para inserir IDs dos produtos durante setup"""
    
    def __init__(self):
        components = [
            ui.TextInput(
                label="IDs dos Produtos",
                placeholder="Ex: 1,2,3,5",
                custom_id="product_ids",
                required=True,
                max_length=200
            )
        ]
        super().__init__(title="Produtos do Ticket", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        product_ids_text = interaction.text_values.get("product_ids", "").strip()
        
        try:
            product_ids = [int(x.strip()) for x in product_ids_text.split(',') if x.strip()]
        except ValueError:
            await interaction.followup.send("❌ IDs inválidos! Use números separados por vírgula (ex: 1,2,3)", ephemeral=True)
            return
        
        # Buscar dados do setup
        setup_data = getattr(interaction.client, '_setup_data', {})
        
        # Criar view de configuração detalhada
        ticket_config_view = TicketConfigView(
            interaction.guild_id,
            ticket_type=setup_data.get('ticket_type', 'payment'),
            mention_role=setup_data.get('mention_role'),
            product_ids=product_ids
        )
        new_embed = ticket_config_view._create_embed()
        
        await interaction.followup.send(
            f"✅ **Produtos configurados:** {', '.join(map(str, product_ids))}\n\nProsseguindo para configurações detalhadas...",
            embed=new_embed,
            view=ticket_config_view,
            ephemeral=True
        )

class ObjectiveSelect(ui.Select):
    """Select menu para escolher o objetivo do ticket"""
    
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="💳 Pagamentos Automatizados",
                description="Sistema de vendas com produtos e pagamento automatizado",
                value="payment"
            ),
            disnake.SelectOption(
                label="🎫 Tickets Manuais",
                description="Atendentes fazem a venda manualmente",
                value="manual"
            ),
            disnake.SelectOption(
                label="❓ Somente Suporte",
                description="Apenas para tirar dúvidas e suporte",
                value="support"
            )
        ]
        
        super().__init__(
            placeholder="🎯 Escolha o objetivo do ticket...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback quando usuário seleciona um objetivo"""
        selected_type = self.values[0]
        
        # Encontrar o label da opção selecionada
        selected_label = "Objetivo"
        for option in self.options:
            if option.value == selected_type:
                selected_label = option.label
                break
        
        # Desabilitar o select após seleção
        self.disabled = True
        
        # Atualizar mensagem inicial
        embed = disnake.Embed(
            title="⚙️ Configuração de Ticket",
            description=f"**Objetivo selecionado:** {selected_label}\n\n✅ Prosseguindo para seleção de cargo...",
            color=0x0099ff
        )
        await interaction.response.edit_message(embed=embed, view=self.view)
        
        # Aguardar um momento
        await asyncio.sleep(1)
        
        # Criar select de cargo
        role_select = RoleSelect(selected_type, interaction.guild)
        role_view = ui.View(timeout=300)
        role_view.add_item(role_select)
        
        embed = disnake.Embed(
            title="👤 Seleção de Cargo",
            description="Escolha o cargo que será mencionado quando o ticket for criado:",
            color=0x0099ff
        )
        await interaction.followup.send(embed=embed, view=role_view, ephemeral=True)

class ObjectiveSelectionView(ui.View):
    """View inicial para selecionar o objetivo do ticket"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)  # 5 minutos
        self.guild_id = guild_id
        self.add_item(ObjectiveSelect())
    
    async def on_timeout(self):
        """Quando o timeout expira"""
        for item in self.children:
            item.disabled = True

class SetupMessageModal(ui.Modal):
    """Modal para criar mensagens embed personalizadas - DISNAKE"""
    
    def __init__(self):
        components = [
            ui.TextInput(
            label="Título", 
            placeholder="Ex: Bem-vindo ao Servidor!", 
                custom_id="titulo",
                required=False,
            max_length=256,
                style=disnake.TextInputStyle.short
            ),
            ui.TextInput(
            label="Descrição", 
            placeholder="Escreva o conteúdo principal da mensagem...", 
                custom_id="descricao",
                required=True,
            max_length=4000,
                style=disnake.TextInputStyle.paragraph
            ),
            ui.TextInput(
            label="URL da Imagem", 
            placeholder="Cole o link da imagem (opcional)", 
                custom_id="url_imagem",
            required=False,
                max_length=500,
                style=disnake.TextInputStyle.short
            ),
            ui.TextInput(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #0099ff ou 0x0099ff", 
                custom_id="cor_hex",
            value="#0099ff",
                max_length=10,
                style=disnake.TextInputStyle.short
            ),
            ui.TextInput(
            label="Rodapé (Footer)", 
            placeholder="Texto no rodapé (opcional)", 
                custom_id="rodape",
            required=False,
                max_length=100,
                style=disnake.TextInputStyle.short
            )
        ]
        super().__init__(title="Criar Mensagem Embed", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        """Processa a criação da mensagem embed"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            start_time = time.time()
            
            # Acessar valores via text_values - muito mais robusto
            titulo = interaction.text_values.get("titulo", "").strip()
            descricao = interaction.text_values.get("descricao", "").strip()
            url_imagem = interaction.text_values.get("url_imagem", "").strip()
            cor_hex = interaction.text_values.get("cor_hex", "#0099ff").strip()
            rodape = interaction.text_values.get("rodape", "").strip()
            
            # Converter cor hex para int
            try:
                cor_hex_clean = cor_hex.strip().lower()
                if cor_hex_clean.startswith('#'):
                    cor_hex_clean = cor_hex_clean[1:]
                elif cor_hex_clean.startswith('0x'):
                    cor_hex_clean = cor_hex_clean[2:]
                if len(cor_hex_clean) == 3:
                    cor_hex_clean = cor_hex_clean[0]*2 + cor_hex_clean[1]*2 + cor_hex_clean[2]*2
                cor_int = int(cor_hex_clean, 16)
            except (ValueError, IndexError):
                cor_int = 0x0099ff
            
            # Criar embed
            embed = disnake.Embed(description=descricao, color=cor_int)
            if titulo:
                embed.title = titulo
            if url_imagem and url_imagem.startswith(('http://', 'https://')):
                    embed.set_image(url=url_imagem)
            if rodape:
                embed.set_footer(text=rodape)
            
            await interaction.followup.send("✅ **Embed criado com sucesso!**", embed=embed, ephemeral=True)
            print(f"⏱️ SetupMessageModal processado em {time.time() - start_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao criar mensagem embed: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro: {str(e)[:200]}", ephemeral=True)

class TicketConfigView(ui.View):
    """View interativa para configurar tickets com preview em tempo real"""
    
    def __init__(self, guild_id: int, ticket_type: str = 'payment', mention_role: int = None, product_ids: list = None):
        super().__init__(timeout=1800)  # 30 minutos
        self.guild_id = guild_id
        
        # Configuração de título e descrição baseado no tipo
        if ticket_type == 'payment':
            default_title = "🛒 Sistema de Vendas Automatizado"
            default_description = "Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!"
            default_button = "Criar Ticket de Compra"
            default_footer = "Atendimento 24/7 • Pagamento via Pix"
        elif ticket_type == 'manual':
            default_title = "🎫 Sistema de Atendimento"
            default_description = "Clique no botão abaixo para criar um ticket e ser atendido por nossa equipe!"
            default_button = "Abrir Ticket"
            default_footer = "Atendimento disponível"
        else:  # support
            default_title = "❓ Central de Suporte"
            default_description = "Clique no botão abaixo para criar um ticket de suporte e esclarecer suas dúvidas!"
            default_button = "Abrir Ticket de Suporte"
            default_footer = "Equipe de suporte disponível"
        
        self.config = {
            'title': default_title,
            'description': default_description,
            'color': 0x0099ff,
            'button_name': default_button,
            'ticket_type': ticket_type,
            'mention_role': mention_role,  # Role ID para mencionar (passado como parâmetro)
            'product_ids': product_ids,  # IDs dos produtos (passado como parâmetro)
            'author': None,
            'thumbnail': None,
            'image': None,
            'footer': default_footer,
            'fields': []
        }
        self.message = None
        
        # Registrar esta view como ativa
        active_config_views[guild_id] = self
        
        # Adicionar botões de configuração
        self.add_item(TitleButton())
        self.add_item(DescriptionButton())
        self.add_item(ColorButton())
        self.add_item(AuthorButton())
        self.add_item(FieldsButton())
        self.add_item(ImageButton())
        self.add_item(FooterButton())
        self.add_item(ButtonNameButton())
        self.add_item(TicketTypeButton())
        self.add_item(MentionRoleButton())
        self.add_item(ProductFilterButton())
        self.add_item(FinishButton())
    
    async def on_timeout(self):
        """Quando o timeout expira"""
        if self.guild_id in active_config_views:
            del active_config_views[self.guild_id]
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)
    
    async def update_preview(self, interaction: disnake.Interaction):
        """Atualiza o preview do embed"""
        try:
            print(f"🔧 update_preview chamado para guild {self.guild_id}")
            
            # Se interaction já foi respondida, apenas editar a mensagem
            if interaction.response.is_done():
                print("🔧 Interaction já respondida, editando mensagem...")
                if self.message:
                    await self.message.edit(embed=self._create_embed(), view=self)
                else:
                    print("❌ self.message é None, não é possível editar")
            else:
                print("🔧 Enviando nova mensagem...")
                self.message = await interaction.response.send_message(embed=self._create_embed(), view=self)
                
        except Exception as e:
            print(f"❌ Erro ao atualizar preview: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_embed(self):
        """Cria o embed baseado na configuração"""
        embed = disnake.Embed(
            title=self.config['title'],
            description=self.config['description'],
            color=self.config['color']
        )
        
        # Adicionar autor se configurado
        if self.config['author']:
            embed.set_author(name=self.config['author'])
        
        # Adicionar thumbnail se configurado
        if self.config['thumbnail']:
            embed.set_thumbnail(url=self.config['thumbnail'])
        
        # Adicionar imagem se configurada
        if self.config['image']:
            embed.set_image(url=self.config['image'])
        
        # Adicionar campos se configurados
        for field in self.config['fields']:
            embed.add_field(
                name=field['name'],
                value=field['value'],
                inline=field.get('inline', False)
            )
        
        # Adicionar rodapé se configurado
        if self.config['footer']:
            embed.set_footer(text=self.config['footer'])
        
        # Adicionar informações sobre tipo de ticket
        ticket_type_names = {
            'payment': '💳 Pagamentos',
            'manual': '🎫 Ticket Manual',
            'support': '❓ Somente Suporte'
        }
        embed.add_field(
            name="🎯 Tipo de Ticket",
            value=ticket_type_names.get(self.config.get('ticket_type', 'payment'), '💳 Pagamentos'),
            inline=True
        )
        
        # Adicionar informações sobre cargo
        if self.config.get('mention_role'):
            embed.add_field(
                name="👤 Cargo a Mencionar",
                value=f"<@&{self.config['mention_role']}>",
                inline=True
            )
        
        # Adicionar informações sobre filtro de produtos (apenas para payment)
        if self.config['product_ids'] and self.config.get('ticket_type') == 'payment':
            embed.add_field(
                name="🔍 Produtos Filtrados",
                value=f"Apenas os produtos com IDs: **{', '.join(map(str, self.config['product_ids']))}** aparecerão neste ticket.",
                inline=False
            )
        
        return embed

    async def finish_configuration(self, interaction: disnake.Interaction):
        """Finaliza a configuração e salva no banco"""
        try:
            print(f"🔧 Finalizando configuração para guild {self.guild_id}")
            
            # Salvar configuração no banco de dados
            from models.guild_config_model import GuildConfigModel
            guild_config = GuildConfigModel()
            
            success = await guild_config.set_ticket_product_filter(
                guild_id=self.guild_id,
                product_ids=self.config['product_ids']
            )
            
            if not success:
                await interaction.response.send_message(
                    "❌ Erro ao salvar configuração no banco de dados.",
                    ephemeral=True
                )
                return
            
            # Criar embed final
            embed = disnake.Embed(
                title=self.config['title'],
                description=self.config['description'],
                color=self.config['color']
            )
            
            # Adicionar autor se configurado
            if self.config['author']:
                embed.set_author(name=self.config['author'])
            
            # Adicionar thumbnail se configurado
            if self.config['thumbnail']:
                embed.set_thumbnail(url=self.config['thumbnail'])
            
            # Adicionar imagem se configurada
            if self.config['image']:
                embed.set_image(url=self.config['image'])
            
            # Adicionar campos se configurados
            for field in self.config['fields']:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field.get('inline', False)
                )
            
            # Adicionar rodapé se configurado
            if self.config['footer']:
                embed.set_footer(text=self.config['footer'])
            
            # Adicionar informações sobre tipo de ticket
            ticket_type_names = {
                'payment': '💳 Pagamentos',
                'manual': '🎫 Ticket Manual',
                'support': '❓ Somente Suporte'
            }
            embed.add_field(
                name="🎯 Tipo de Ticket",
                value=ticket_type_names.get(self.config.get('ticket_type', 'payment'), '💳 Pagamentos'),
                inline=True
            )
            
            # Adicionar informações sobre cargo
            if self.config.get('mention_role'):
                embed.add_field(
                    name="👤 Cargo a Mencionar",
                    value=f"<@&{self.config['mention_role']}>",
                    inline=True
                )
            
            # Adicionar informações sobre filtro de produtos (apenas para payment)
            if self.config['product_ids'] and self.config.get('ticket_type') == 'payment':
                embed.add_field(
                    name="🔍 Produtos Filtrados",
                    value=f"Apenas os produtos com IDs: **{', '.join(map(str, self.config['product_ids']))}** aparecerão neste ticket.",
                    inline=False
                )
            
            # Criar view com botão de ticket
            ticket_view = TicketView(self.config['button_name'])
            
            # Enviar mensagem final
            await interaction.response.send_message(embed=embed, view=ticket_view)
            print("✅ Configuração finalizada com sucesso!")
            
            # Remover view das ativas
            if self.guild_id in active_config_views:
                del active_config_views[self.guild_id]
            
        except Exception as e:
            print(f"❌ Erro ao finalizar configuração: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Erro ao finalizar configuração.",
                ephemeral=True
            )

class TitleModal(ui.Modal):
    """Modal para editar título"""
    
    def __init__(self, current_title: str):
        components = [
            ui.TextInput(
                label="Título do Embed",
                placeholder="Ex: 🛒 Sistema de Vendas Automatizado",
                custom_id="title_input",
                value=current_title,
                max_length=256
            )
        ]
        super().__init__(title="Editar Título", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        title = interaction.text_values.get("title_input", "").strip()
        
        # Buscar view ativa
        view = active_config_views.get(interaction.guild_id)
        print(f"🔧 TitleModal: view encontrada? {view is not None}")
        if view:
            print(f"🔧 TitleModal: view.message existe? {view.message is not None}")
            view.config['title'] = title
            if view.message:
                print("🔧 Editando mensagem...")
                await view.message.edit(embed=view._create_embed(), view=view)
                print("✅ Mensagem editada com sucesso!")
            else:
                print("❌ view.message é None, tentando buscar mensagem...")
                # Tentar buscar mensagem recente do canal
                messages = await interaction.channel.history(limit=5).flatten()
                for msg in messages:
                    if msg.author.id == interaction.client.user.id and msg.embeds:
                        view.message = msg
                        await view.message.edit(embed=view._create_embed(), view=view)
                        print("✅ Mensagem editada via fallback!")
                        break
            await interaction.followup.send("✅ Título atualizado!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada. Use `/setup_ticket` novamente.", ephemeral=True)

class TitleButton(ui.Button):
    """Botão para editar título"""
    
    def __init__(self):
        super().__init__(
            label="Título",
            style=disnake.ButtonStyle.secondary,
            emoji="📝",
            custom_id="edit_title"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_title = view.config.get('title', '🛒 Sistema de Vendas Automatizado')
        modal = TitleModal(current_title)
        await interaction.response.send_modal(modal)

class DescriptionModal(ui.Modal):
    """Modal para editar descrição"""
    
    def __init__(self, current_description: str):
        components = [
            ui.TextInput(
                label="Descrição do Embed",
                placeholder="Clique no botão abaixo para criar um ticket!",
                custom_id="description_input",
                value=current_description,
                style=disnake.TextInputStyle.paragraph,
                max_length=4000
            )
        ]
        super().__init__(title="Editar Descrição", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        description = interaction.text_values.get("description_input", "").strip()
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['description'] = description
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Descrição atualizada!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class DescriptionButton(ui.Button):
    """Botão para editar descrição"""
    
    def __init__(self):
        super().__init__(
            label="Descrição",
            style=disnake.ButtonStyle.secondary,
            emoji="📄",
            custom_id="edit_description"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_desc = view.config.get('description', 'Clique no botão abaixo!')
        modal = DescriptionModal(current_desc)
        await interaction.response.send_modal(modal)

class CustomColorModal(ui.Modal):
    """Modal para inserir cor personalizada (hex)"""
    
    def __init__(self):
        components = [
            ui.TextInput(
                label="Cor do Embed (Hex)",
                placeholder="Ex: #0099ff ou 0099ff",
                custom_id="color_input",
                value="#0099ff",
                max_length=10
            )
        ]
        super().__init__(title="Cor Personalizada", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        color_hex = interaction.text_values.get("color_input", "#0099ff").strip()
        
        try:
            # Converter cor hex para int
            cor_hex_clean = color_hex.strip().lower()
            if cor_hex_clean.startswith('#'):
                cor_hex_clean = cor_hex_clean[1:]
            elif cor_hex_clean.startswith('0x'):
                cor_hex_clean = cor_hex_clean[2:]
            if len(cor_hex_clean) == 3:
                cor_hex_clean = cor_hex_clean[0]*2 + cor_hex_clean[1]*2 + cor_hex_clean[2]*2
            cor_int = int(cor_hex_clean, 16)
            
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['color'] = cor_int
                if view.message:
                    await view.message.edit(embed=view._create_embed(), view=view)
                await interaction.followup.send("✅ Cor personalizada aplicada!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)
        except ValueError:
            await interaction.followup.send("❌ Cor inválida! Use formato hex (#0099ff).", ephemeral=True)

class ColorSelect(ui.Select):
    """Select menu para escolher cor"""
    
    def __init__(self):
        # Cores padrão do Discord
        colors = [
            ("Default", "#5865F2", "Cor padrão do Discord"),
            ("Verde", "#57F287", "Verde sucesso"),
            ("Amarelo", "#FEE75C", "Amarelo alerta"),
            ("Fuchsia", "#EB459E", "Rosa vibrante"),
            ("Vermelho", "#ED4245", "Vermelho erro"),
            ("Branco", "#FFFFFF", "Branco puro"),
            ("Cinza", "#95A5A6", "Cinza neutro"),
            ("Azul Claro", "#3498DB", "Azul céu"),
            ("Azul Escuro", "#206694", "Azul marinho"),
            ("Verde Escuro", "#1F8B4C", "Verde floresta"),
            ("Laranja", "#F39C12", "Laranja"),
            ("Roxo", "#9B59B6", "Roxo"),
            ("Personalizada", "custom", "Inserir código hex personalizado"),
        ]
        
        options = []
        for name, value, description in colors:
            options.append(disnake.SelectOption(
                label=name,
                description=description,
                value=value,
                emoji="🎨" if name == "Personalizada" else None
            ))
        
        super().__init__(
            placeholder="Escolha uma cor...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback quando usuário seleciona uma cor"""
        selected_color = self.values[0]
        
        if selected_color == "custom":
            # Abrir modal para cor personalizada
            modal = CustomColorModal()
            await interaction.response.send_modal(modal)
        else:
            # Usar cor pré-definida
            try:
                # Converter cor hex para int
                cor_hex_clean = selected_color.strip().lower().lstrip('#')
                if len(cor_hex_clean) == 3:
                    cor_hex_clean = cor_hex_clean[0]*2 + cor_hex_clean[1]*2 + cor_hex_clean[2]*2
                cor_int = int(cor_hex_clean, 16)
                
                view = active_config_views.get(interaction.guild_id)
                if view:
                    view.config['color'] = cor_int
                    if view.message:
                        await view.message.edit(embed=view._create_embed(), view=view)
                    await interaction.response.send_message("✅ Cor atualizada!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Sessão expirada.", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ Erro ao processar cor.", ephemeral=True)

class ColorButton(ui.Button):
    """Botão para editar cor"""
    
    def __init__(self):
        super().__init__(
            label="Cor",
            style=disnake.ButtonStyle.secondary,
            emoji="🎨",
            custom_id="edit_color"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        # Criar view temporária com select menu de cores
        view = ui.View(timeout=60)
        select = ColorSelect()
        view.add_item(select)
        
        await interaction.response.send_message(
            "🎨 **Escolha uma cor:**",
            view=view,
            ephemeral=True
        )

class AuthorModal(ui.Modal):
    """Modal para editar autor"""
    
    def __init__(self, current_author: str):
        components = [
            ui.TextInput(
                label="Nome do Autor (opcional)",
                placeholder="Deixe vazio para remover",
                custom_id="author_input",
                value=current_author or "",
                required=False,
                max_length=100
            )
        ]
        super().__init__(title="Editar Autor", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        author = interaction.text_values.get("author_input", "").strip() or None
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['author'] = author
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Autor atualizado!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class AuthorButton(ui.Button):
    """Botão para editar autor"""
    
    def __init__(self):
        super().__init__(
            label="Autor",
            style=disnake.ButtonStyle.secondary,
            emoji="👤",
            custom_id="edit_author"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_author = view.config.get('author') or ""
        modal = AuthorModal(current_author)
        await interaction.response.send_modal(modal)

class FieldsModal(ui.Modal):
    """Modal para editar campos"""
    
    def __init__(self, current_fields: list):
        # Converter campos para texto
        fields_text = ""
        if current_fields:
            for field in current_fields:
                fields_text += f"{field['name']}|{field['value']}|{field.get('inline', False)}\n"
        
        components = [
            ui.TextInput(
                label="Campos (um por linha)",
                placeholder="Nome|Valor|inline",
                custom_id="fields_input",
                value=fields_text.strip(),
                style=disnake.TextInputStyle.paragraph,
                max_length=2000,
                required=False
            )
        ]
        super().__init__(title="Editar Campos", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        fields_text = interaction.text_values.get("fields_input", "").strip()
        fields = []
        
        if fields_text:
            for line in fields_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 2:
                    fields.append({
                        'name': parts[0].strip(),
                        'value': parts[1].strip(),
                        'inline': parts[2].strip().lower() == 'true' if len(parts) > 2 else False
                    })
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['fields'] = fields
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Campos atualizados!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class FieldsButton(ui.Button):
    """Botão para editar campos"""
    
    def __init__(self):
        super().__init__(
            label="Campos",
            style=disnake.ButtonStyle.secondary,
            emoji="📋",
            custom_id="edit_fields"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_fields = view.config.get('fields', [])
        modal = FieldsModal(current_fields)
        await interaction.response.send_modal(modal)

class ImageModal(ui.Modal):
    """Modal para editar imagens"""
    
    def __init__(self, current_image: str, current_thumbnail: str):
        images_text = f"{current_image or ''}\n{current_thumbnail or ''}"
        
        components = [
            ui.TextInput(
                label="URLs das Imagens",
                placeholder="Linha 1: imagem principal\nLinha 2: thumbnail",
                custom_id="images_input",
                value=images_text.strip(),
                style=disnake.TextInputStyle.paragraph,
                max_length=1000,
                required=False
            )
        ]
        super().__init__(title="Editar Imagens", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        images_text = interaction.text_values.get("images_input", "").strip()
        lines = images_text.split('\n')
        
        image = lines[0].strip() if len(lines) > 0 and lines[0].strip() else None
        thumbnail = lines[1].strip() if len(lines) > 1 and lines[1].strip() else None
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['image'] = image
            view.config['thumbnail'] = thumbnail
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Imagens atualizadas!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class ImageButton(ui.Button):
    """Botão para editar imagens"""
    
    def __init__(self):
        super().__init__(
            label="Imagens",
            style=disnake.ButtonStyle.secondary,
            emoji="🖼️",
            custom_id="edit_images"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_image = view.config.get('image') or ""
        current_thumbnail = view.config.get('thumbnail') or ""
        modal = ImageModal(current_image, current_thumbnail)
        await interaction.response.send_modal(modal)

class FooterModal(ui.Modal):
    """Modal para editar rodapé"""
    
    def __init__(self, current_footer: str):
        components = [
            ui.TextInput(
                label="Texto do Rodapé (opcional)",
                placeholder="Deixe vazio para remover",
                custom_id="footer_input",
                value=current_footer or "",
                required=False,
                max_length=100
            )
        ]
        super().__init__(title="Editar Rodapé", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        footer = interaction.text_values.get("footer_input", "").strip() or None
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['footer'] = footer
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Rodapé atualizado!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class FooterButton(ui.Button):
    """Botão para editar rodapé"""
    
    def __init__(self):
        super().__init__(
            label="Rodapé",
            style=disnake.ButtonStyle.secondary,
            emoji="🏷️",
            custom_id="edit_footer"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_footer = view.config.get('footer') or ""
        modal = FooterModal(current_footer)
        await interaction.response.send_modal(modal)

class ButtonNameModal(ui.Modal):
    """Modal para editar nome do botão"""
    
    def __init__(self, current_button_name: str):
        components = [
            ui.TextInput(
                label="Nome do Botão",
                placeholder="Ex: Criar Ticket de Compra",
                custom_id="button_name_input",
                value=current_button_name,
                max_length=80
            )
        ]
        super().__init__(title="Editar Nome do Botão", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        button_name = interaction.text_values.get("button_name_input", "").strip()
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['button_name'] = button_name
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Nome do botão atualizado!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class ButtonNameButton(ui.Button):
    """Botão para editar nome do botão"""
    
    def __init__(self):
        super().__init__(
            label="Botão",
            style=disnake.ButtonStyle.secondary,
            emoji="🔘",
            custom_id="edit_button"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_button_name = view.config.get('button_name', 'Criar Ticket de Compra')
        modal = ButtonNameModal(current_button_name)
        await interaction.response.send_modal(modal)

class ProductFilterModal(ui.Modal):
    """Modal para editar filtro de produtos"""
    
    def __init__(self, current_product_ids: list):
        product_ids_text = ""
        if current_product_ids:
            product_ids_text = ",".join(map(str, current_product_ids))
        
        components = [
            ui.TextInput(
                label="IDs dos Produtos (opcional)",
                placeholder="Ex: 1,2,3,5 ou deixe vazio para todos",
                custom_id="product_ids_input",
                value=product_ids_text,
                required=False,
                max_length=200
            )
        ]
        super().__init__(title="Editar Filtro de Produtos", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        product_ids_text = interaction.text_values.get("product_ids_input", "").strip()
        product_ids = None
        
        if product_ids_text:
            try:
                product_ids = [int(x.strip()) for x in product_ids_text.split(',') if x.strip()]
            except ValueError:
                await interaction.followup.send("❌ IDs inválidos! Use números separados por vírgula.", ephemeral=True)
                return
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['product_ids'] = product_ids
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send("✅ Filtro de produtos atualizado!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class ProductFilterButton(ui.Button):
    """Botão para editar filtro de produtos"""
    
    def __init__(self):
        super().__init__(
            label="Produtos",
            style=disnake.ButtonStyle.secondary,
            emoji="🛍️",
            custom_id="edit_products"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_product_ids = view.config.get('product_ids') or []
        modal = ProductFilterModal(current_product_ids)
        await interaction.response.send_modal(modal)

class TicketTypeSelect(ui.Select):
    """Select menu para escolher tipo de ticket"""
    
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="💳 Pagamentos",
                description="Sistema automatizado com produtos",
                value="payment"
            ),
            disnake.SelectOption(
                label="🎫 Ticket Manual",
                description="Atendente faz a venda manualmente",
                value="manual"
            ),
            disnake.SelectOption(
                label="❓ Somente Suporte",
                description="Apenas para tirar dúvidas",
                value="support"
            )
        ]
        
        super().__init__(
            placeholder="Escolha o tipo de ticket...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback quando usuário seleciona um tipo"""
        selected_type = self.values[0]
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['ticket_type'] = selected_type
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.response.send_message("✅ Tipo de ticket atualizado!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Sessão expirada.", ephemeral=True)

class TicketTypeButton(ui.Button):
    """Botão para editar tipo de ticket"""
    
    def __init__(self):
        super().__init__(
            label="Tipo",
            style=disnake.ButtonStyle.secondary,
            emoji="🎯",
            custom_id="edit_ticket_type"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        # Criar view temporária com select menu
        view = ui.View(timeout=60)
        select = TicketTypeSelect()
        view.add_item(select)
        
        await interaction.response.send_message(
            "🎯 **Escolha o tipo de ticket:**",
            view=view,
            ephemeral=True
        )

class MentionRoleModal(ui.Modal):
    """Modal para editar role a mencionar"""
    
    def __init__(self, current_role_mention: str = ""):
        components = [
            ui.TextInput(
                label="Nome ou ID do Cargo",
                placeholder="Ex: @Atendente ou 1234567890",
                custom_id="role_input",
                value=current_role_mention or "",
                required=False,
                max_length=100
            )
        ]
        super().__init__(title="Editar Cargo a Mencionar", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        role_input = interaction.text_values.get("role_input", "").strip()
        
        # Tentar encontrar o role
        role_id = None
        if role_input:
            # Procurar por ID
            if role_input.isdigit():
                role = interaction.guild.get_role(int(role_input))
                if role:
                    role_id = role.id
            else:
                # Procurar por nome
                role = disnake.utils.get(interaction.guild.roles, name=role_input)
                if role:
                    role_id = role.id
                else:
                    await interaction.followup.send("❌ Cargo não encontrado!", ephemeral=True)
                    return
            
            if not role_id:
                await interaction.followup.send("❌ Cargo inválido!", ephemeral=True)
                return
        
        view = active_config_views.get(interaction.guild_id)
        if view:
            view.config['mention_role'] = role_id
            if view.message:
                await view.message.edit(embed=view._create_embed(), view=view)
            await interaction.followup.send(f"✅ Cargo atualizado! {f'<@&{role_id}>' if role_id else '(nenhum)'}", ephemeral=True)
        else:
            await interaction.followup.send("❌ Sessão expirada.", ephemeral=True)

class MentionRoleButton(ui.Button):
    """Botão para editar cargo a mencionar"""
    
    def __init__(self):
        super().__init__(
            label="Cargo",
            style=disnake.ButtonStyle.secondary,
            emoji="👤",
            custom_id="edit_mention_role"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        current_role_id = view.config.get('mention_role')
        current_role_mention = ""
        if current_role_id:
            current_role_mention = f"<@&{current_role_id}>"
        modal = MentionRoleModal(current_role_mention)
        await interaction.response.send_modal(modal)

class FinishButton(ui.Button):
    """Botão para finalizar configuração"""
    
    def __init__(self):
        super().__init__(
            label="Finalizar",
            style=disnake.ButtonStyle.success,
            emoji="✅",
            custom_id="finish_config"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        view = self.view
        await view.finish_configuration(interaction)



class SetupTicketModal(ui.Modal):
    """Modal para configurar o sistema de tickets"""
    
    def __init__(self):
        components = [
            ui.TextInput(
                label="Headline",
                placeholder="Ex: Sistema de Vendas Automatizado",
                custom_id="headline",
                value="🛒 Sistema de Vendas Automatizado",
                max_length=100
            ),
            ui.TextInput(
                label="Descrição",
                placeholder="Ex: Clique no botão abaixo para criar um ticket de compra",
                custom_id="descricao",
                value="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
                style=disnake.TextInputStyle.paragraph,
                max_length=1000
            ),
            ui.TextInput(
                label="IDs dos Produtos (vazio = todos)",
                placeholder="Ex: 1,2,3,5 ou deixe vazio para todos",
                custom_id="product_ids",
                value="",
                required=False,
                max_length=200
            ),
            ui.TextInput(
                label="Nome do Botão",
                placeholder="Ex: Criar Ticket de Compra",
                custom_id="nome_botao",
                value="Criar Ticket de Compra",
                max_length=80
            ),
            ui.TextInput(
                label="Cor do Embed (Hex)",
                placeholder="Ex: #0099ff ou 0x0099ff",
                custom_id="cor",
                value="#0099ff",
                max_length=10
            )
        ]
        super().__init__(title="Configurar Sistema de Tickets", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        """Processa a configuração do sistema de tickets"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            import asyncio
            from models.guild_config_model import GuildConfigModel
            
            start_time = time.time()
            
            # Acessar valores via interaction.text_values
            headline = interaction.text_values.get("headline", "🛒 Sistema de Vendas").strip()
            descricao = interaction.text_values.get("descricao", "Clique no botão abaixo!").strip()
            product_ids_input = interaction.text_values.get("product_ids", "").strip()
            nome_botao = interaction.text_values.get("nome_botao", "Criar Ticket de Compra").strip()
            cor_hex = interaction.text_values.get("cor", "#0099ff").strip()
            
            # Processar IDs dos produtos
            allowed_product_ids = None
            if product_ids_input:
                try:
                    allowed_product_ids = [int(pid.strip()) for pid in product_ids_input.split(',') if pid.strip()]
                except ValueError:
                    await interaction.followup.send("❌ IDs de produtos inválidos! Use números separados por vírgula (ex: 1,2,3)", ephemeral=True)
                    return

            # Salvar configuração no banco
            guild_config = GuildConfigModel()
            try:
                success = await asyncio.wait_for(
                    guild_config.set_ticket_product_filter(
                    guild_id=interaction.guild_id,
                    product_ids=allowed_product_ids
                    ),
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ **Timeout!** O banco demorou muito. Tente novamente.", ephemeral=True)
                return
            
            if not success:
                await interaction.followup.send("❌ Erro ao salvar configuração no banco de dados.", ephemeral=True)
                return

            # Converter cor hex para int
            try:
                cor_hex_clean = cor_hex.strip().lower()
                if cor_hex_clean.startswith('#'):
                    cor_hex_clean = cor_hex_clean[1:]
                elif cor_hex_clean.startswith('0x'):
                    cor_hex_clean = cor_hex_clean[2:]
                if len(cor_hex_clean) == 3:
                    cor_hex_clean = cor_hex_clean[0]*2 + cor_hex_clean[1]*2 + cor_hex_clean[2]*2
                cor_int = int(cor_hex_clean, 16)
            except (ValueError, IndexError):
                cor_int = 0x0099ff
            
            # Criar embed
            embed = disnake.Embed(title=headline, description=descricao, color=cor_int)
            embed.add_field(
                name="🚀 Como Funciona?",
                value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
                inline=False
            )
            if allowed_product_ids:
                embed.add_field(
                    name="🔍 Produtos Filtrados",
                    value=f"Apenas os produtos com IDs: **{', '.join(map(str, allowed_product_ids))}** aparecerão neste ticket.",
                    inline=False
                )
            embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")

            # Criar view com botão
            view = TicketView(nome_botao)
            await interaction.followup.send(
                "✅ **Sistema configurado com sucesso!**\nCopie e cole abaixo:",
                embed=embed,
                view=view,
                ephemeral=True
            )
            
            print(f"⏱️ SetupTicketModal processado em {time.time() - start_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao configurar sistema de tickets: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro: {str(e)[:200]}", ephemeral=True)

class CouponInputModal(ui.Modal):
    """Modal para coletar código de cupom (opcional) - DISNAKE"""
    
    def __init__(self, user, guild, product):
        self.user = user
        self.guild = guild
        self.product = product
        
        components = [
            ui.TextInput(
            label="Código do Cupom",
            placeholder="Digite o código do cupom ou deixe em branco",
                custom_id="coupon_code",
            required=False,
                max_length=50,
                style=disnake.TextInputStyle.short
            )
        ]
        super().__init__(title="Cupom de Desconto (Opcional)", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        """Processa o cupom e cria o ticket"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            start_time = time.time()
            
            # Acessar valor via text_values - mais robusto
            coupon_code = interaction.text_values.get("coupon_code", "").strip() or None
            
            from utils.ticket_manager import TicketManager
            ticket_manager = TicketManager(interaction.client)
            
            success, message = await ticket_manager.create_ticket(
                self.user,
                self.guild,
                self.product,
                coupon_code=coupon_code
            )
            
            if success:
                await interaction.followup.send(f"✅ {message}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ {message}", ephemeral=True)
            
            print(f"⏱️ CouponInputModal processado em {time.time() - start_time:.2f}s")
                
        except Exception as e:
            print(f"❌ Erro ao processar cupom: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ **Erro ao processar cupom:** {str(e)[:200]}",
                ephemeral=True
            )
    
    async def on_error(self, error: Exception, interaction: disnake.ModalInteraction):
        """Handler de erros do modal"""
        print(f"❌ Erro no CouponInputModal: {error}")
        import traceback
        traceback.print_exc()
        
        try:
            await interaction.followup.send(
                f"❌ **Erro inesperado:** {str(error)[:200]}",
                ephemeral=True
            )
        except:
            pass

class ProductSelect(ui.Select):
    """Select menu personalizado para escolher produto"""
    
    def __init__(self, products: List[Dict], options: List[disnake.SelectOption]):
        super().__init__(
            placeholder="Escolha um produto...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.products = products
    
    async def callback(self, interaction: disnake.Interaction):
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
            except disnake.errors.NotFound:
                pass

class ProductSelectView(ui.View):
    """View com select menu para escolher produto"""
    
    def __init__(self, products: List[Dict]):
        super().__init__(timeout=600)
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
            option = disnake.SelectOption(
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
            style=disnake.ButtonStyle.primary,
            emoji="🎫",
            custom_id="create_ticket_button"
        )
        self.product_model = ProductModel()
    
    async def callback(self, interaction: disnake.Interaction):
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
            
            # Carregar produtos disponíveis (apenas do servidor atual)
            print(f"🔧 Debug: Tentando carregar produtos do servidor {interaction.guild_id}...")
            products = await self.product_model.get_products_by_guild(interaction.guild_id)
            print(f"🔧 Debug: Produtos carregados: {len(products) if products else 0}")
            
            if not products:
                await interaction.response.send_message(
                    "❌ Nenhum produto disponível no momento.",
                    ephemeral=True
                )
                return
            
            # Aplicar filtro de produtos se configurado
            from models.guild_config_model import GuildConfigModel
            guild_config = GuildConfigModel()
            allowed_product_ids = await guild_config.get_allowed_products(interaction.guild_id)
            
            if allowed_product_ids:
                # Filtrar apenas produtos permitidos
                products = [p for p in products if p['id'] in allowed_product_ids]
                print(f"🔍 Debug: Filtro aplicado - {len(products)} produtos após filtro (IDs permitidos: {allowed_product_ids})")
                
                if not products:
                    await interaction.response.send_message(
                        "❌ Nenhum produto disponível neste ticket no momento.",
                        ephemeral=True
                    )
                    return
            
            # Criar view com select menu
            view = ProductSelectView(products)
            
            embed = disnake.Embed(
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
            style=disnake.ButtonStyle.danger,
            emoji="❌",
            custom_id="close_ticket_button"
        )
    
    async def callback(self, interaction: disnake.Interaction):
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
        components = [
            ui.TextInput(
                label="Código do Cupom",
                placeholder="Ex: PRIMEIRACOMPRA",
                custom_id="code",
                max_length=50,
                required=True
            ),
            ui.TextInput(
                label="Desconto (%)",
                placeholder="Ex: 10 para 10%",
                custom_id="discount",
                max_length=5,
                required=True
            ),
            ui.TextInput(
                label="Limite de Usos (0 = ilimitado)",
                placeholder="Ex: 100",
                custom_id="max_uses",
                value="0",
                max_length=10,
                required=False
            ),
            ui.TextInput(
                label="Um uso por usuário? (sim/nao)",
                placeholder="sim ou nao",
                custom_id="one_per_user",
                value="nao",
                max_length=3,
                required=False
            ),
            ui.TextInput(
                label="Data Expiração (DD/MM/YYYY ou vazio)",
                placeholder="31/12/2025",
                custom_id="expires",
                required=False,
                max_length=10
            )
        ]
        super().__init__(title="Criar Novo Cupom", components=components)
    
    async def callback(self, interaction: disnake.ModalInteraction):
        """Processa criação do cupom"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from models.coupon_model import CouponModel
            from datetime import datetime
            import asyncio
            import time
            
            start_time = time.time()
            
            # Acessar valores via interaction.text_values
            code = interaction.text_values.get("code", "").upper().strip()
            discount_str = interaction.text_values.get("discount", "0").strip()
            max_uses_str = interaction.text_values.get("max_uses", "0").strip()
            one_per_user_str = interaction.text_values.get("one_per_user", "nao").strip()
            expires_str = interaction.text_values.get("expires", "").strip()
            
            # Convert
            try:
                discount = float(discount_str)
            except ValueError:
                await interaction.followup.send("❌ Desconto inválido! Use apenas números (ex: 10)", ephemeral=True)
                return
            
            max_uses = int(max_uses_str) if max_uses_str and max_uses_str != "0" else None
            one_per_user = one_per_user_str.lower() == "sim"
            
            # Validar desconto
            if discount < 1 or discount > 100:
                await interaction.followup.send("❌ Desconto deve estar entre 1% e 100%!", ephemeral=True)
                return
            
            # Processar data de expiração
            expires_at = None
            if expires_str:
                try:
                    expires_at = datetime.strptime(expires_str, "%d/%m/%Y").isoformat()
                except:
                    await interaction.followup.send("❌ Data inválida! Use formato DD/MM/YYYY", ephemeral=True)
                    return
            
            # Criar cupom
            coupon_model = CouponModel()
            coupon_data = {
                'code': code,
                'discount_percent': discount,
                'max_uses': max_uses,
                'one_per_user': one_per_user,
                'expires_at': expires_at,
                'created_by': interaction.user.id,
                'active': True
            }
            
            success, message = await asyncio.wait_for(
                coupon_model.create_coupon(coupon_data),
                timeout=10.0
            )
            
            if success:
                embed = disnake.Embed(
                    title="✅ Cupom Criado!",
                    description=f"Cupom **{code}** criado com sucesso!",
                    color=0x00ff00
                )
                embed.add_field(name="Desconto", value=f"{discount}%", inline=True)
                embed.add_field(name="Limite", value=str(max_uses) if max_uses else "Ilimitado", inline=True)
                embed.add_field(name="Um por usuário", value="Sim" if one_per_user else "Não", inline=True)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(f"❌ {message}", ephemeral=True)
            
            print(f"⏱️ CreateCouponModal processado em {time.time() - start_time:.2f}s")
                
        except (ValueError, asyncio.TimeoutError) as e:
            await interaction.followup.send(f"❌ Erro: {str(e)[:100]}", ephemeral=True)
        except Exception as e:
            print(f"❌ Erro ao criar cupom: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro inesperado: {str(e)[:100]}", ephemeral=True)

class SetupSupportModal(ui.Modal):
    """Modal para configurar o sistema de tickets de suporte com select menu"""
    
    def __init__(self):
        components = [
            ui.TextInput(
                label="Título da Mensagem",
                placeholder="Ex: Central de Atendimento",
                custom_id="titulo",
                value="🎫 Central de Atendimento",
                max_length=100
            ),
            ui.TextInput(
                label="Descrição da Mensagem",
                placeholder="Ex: Clique no botão abaixo para abrir um ticket",
                custom_id="descricao",
                value="Clique no botão abaixo e selecione o tipo de atendimento que você precisa.",
                max_length=1000
            ),
            ui.TextInput(
                label="Opções Menu (EMOJI|Nome|Descrição)",
                placeholder="Uma por linha",
                custom_id="opcoes",
                value="❤️|Parcerias|Para os interessados em colaborar conosco.\n💡|Dúvidas|Caso esteja com dúvidas em algo, abra um ticket.\n✅|Denúncias|Realize denúncias através desse ticket.\n🎁|Sorteios|Aqui você poderá resgatar sua premiação de sorteios.",
                style=disnake.TextInputStyle.paragraph,
                max_length=1000,
                required=True
            ),
            ui.TextInput(
                label="Nome do Botão | Emoji (opcional)",
                placeholder="Ex: Abrir Ticket | 🎫",
                custom_id="botao",
                value="Abrir Ticket | 🎫",
                max_length=100
            ),
            ui.TextInput(
                label="Cor do Embed (Hex)",
                placeholder="Ex: #5865F2",
                custom_id="cor",
                value="#5865F2",
                max_length=10
            )
        ]
        super().__init__(title="Configurar Tickets de Suporte", components=components)

    async def callback(self, interaction: disnake.ModalInteraction):
        """Processa a configuração do sistema de tickets de suporte"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            import time
            start_time = time.time()
            
            # Acessar valores via interaction.text_values
            titulo = interaction.text_values.get("titulo", "🎫 Central de Atendimento").strip()
            descricao = interaction.text_values.get("descricao", "Clique no botão abaixo!").strip()
            opcoes_text = interaction.text_values.get("opcoes", "").strip()
            botao_config = interaction.text_values.get("botao", "Abrir Ticket | 🎫").strip()
            cor_hex = interaction.text_values.get("cor", "#5865F2").strip()
            
            # Processar configuração do botão
            label_botao = "Abrir Ticket"
            emoji_botao = "🎫"
            if botao_config and '|' in botao_config:
                partes_botao = botao_config.split('|')
                if len(partes_botao) >= 2:
                    label_botao = partes_botao[0].strip()
                    emoji_botao = partes_botao[1].strip()
            elif botao_config:
                label_botao = botao_config.strip()
            
            # Processar opções do menu
            opcoes_config = []
            for linha in opcoes_text.split('\n'):
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split('|')
                if len(partes) >= 3:
                    opcoes_config.append({
                        'emoji': partes[0].strip(),
                        'nome': partes[1].strip(),
                        'descricao': partes[2].strip()
                    })
                elif len(partes) == 2:
                    opcoes_config.append({
                        'emoji': partes[0].strip(),
                        'nome': partes[1].strip(),
                        'descricao': f"Abrir ticket de {partes[1].strip().lower()}"
                    })
            
            if not opcoes_config:
                await interaction.followup.send("❌ Nenhuma opção válida configurada! Use o formato: EMOJI|Nome|Descrição", ephemeral=True)
                return
            
            if len(opcoes_config) > 25:
                await interaction.followup.send("❌ Máximo de 25 opções permitidas no select menu!", ephemeral=True)
                return
            
            # Converter cor hex para int
            try:
                cor_hex_clean = cor_hex.strip().lower()
                if cor_hex_clean.startswith('#'):
                    cor_hex_clean = cor_hex_clean[1:]
                elif cor_hex_clean.startswith('0x'):
                    cor_hex_clean = cor_hex_clean[2:]
                if len(cor_hex_clean) == 3:
                    cor_hex_clean = cor_hex_clean[0]*2 + cor_hex_clean[1]*2 + cor_hex_clean[2]*2
                cor_int = int(cor_hex_clean, 16)
            except (ValueError, IndexError):
                cor_int = 0x5865F2
            
            # Criar embed
            embed = disnake.Embed(title=titulo, description=descricao if descricao else None, color=cor_int)
            for opt in opcoes_config:
                embed.add_field(name=f"{opt['emoji']} {opt['nome']}", value=opt['descricao'], inline=False)
            
            # Criar view
            view = MultiSupportTicketView(opcoes_config, label_botao, emoji_botao)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
            print(f"⏱️ SetupSupportModal processado em {time.time() - start_time:.2f}s - {len(opcoes_config)} opções")
            
        except Exception as e:
            print(f"❌ Erro ao configurar sistema de suporte: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro: {str(e)[:100]}", ephemeral=True)

class CustomSupportTicketButton(ui.Button):
    """Botão customizado para criar ticket de suporte com categoria específica"""
    
    def __init__(self, emoji: str, nome: str, categoria: str):
        super().__init__(
            label=nome,
            style=disnake.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"support_ticket_{nome.lower().replace(' ', '_')}"
        )
        self.categoria = categoria
        self.nome_ticket = nome
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback do botão - cria ticket de suporte com categoria"""
        try:
            # Verificar se usuário já tem ticket ativo
            import bot
            if interaction.user.id in bot.active_tickets:
                await interaction.response.send_message(
                    "❌ Você já possui um ticket ativo. Use o canal do seu ticket para continuar.",
                    ephemeral=True
                )
                return
            
            # Criar ticket de suporte com categoria
            ticket_manager = TicketManager()
            success, message = await ticket_manager.create_support_ticket(
                interaction.user,
                interaction.guild,
                categoria=self.categoria
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

class SupportTicketButton(ui.Button):
    """Botão para criar ticket de suporte (versão simples)"""
    
    def __init__(self, nome_botao="Abrir Ticket de Suporte"):
        super().__init__(
            label=nome_botao,
            style=disnake.ButtonStyle.danger,
            emoji="🆘",
            custom_id="create_support_ticket_button"
        )
    
    async def callback(self, interaction: disnake.Interaction):
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

class SupportCategorySelect(ui.Select):
    """Select menu para escolher categoria de suporte"""
    
    def __init__(self, categorias: list):
        # Criar opções do select menu
        options = []
        for cat in categorias:
            options.append(disnake.SelectOption(
                label=cat['nome'],
                description=cat['descricao'][:100],  # Discord limita a 100 chars
                emoji=cat['emoji']
            ))
        
        super().__init__(
            placeholder="Selecione o tipo de atendimento...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="support_category_select"
        )
        self.categorias = categorias
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback quando usuário seleciona uma categoria"""
        try:
            # Pegar categoria selecionada
            categoria_nome = self.values[0]
            
            # Verificar se usuário já tem ticket ativo
            import bot
            if interaction.user.id in bot.active_tickets:
                await interaction.response.send_message(
                    "❌ Você já possui um ticket ativo. Use o canal do seu ticket para continuar.",
                    ephemeral=True
                )
                return
            
            # Criar ticket com categoria
            ticket_manager = TicketManager()
            success, message = await ticket_manager.create_support_ticket(
                interaction.user,
                interaction.guild,
                categoria=categoria_nome
            )
            
            if success:
                await interaction.response.send_message(f"✅ {message}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            print(f"❌ Erro no select de categoria: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Erro ao criar ticket. Tente novamente.",
                ephemeral=True
            )

class SupportSelectButton(ui.Button):
    """Botão que abre o select menu de categorias"""
    
    def __init__(self, label: str, emoji: str, categorias: list):
        super().__init__(
            label=label,
            style=disnake.ButtonStyle.primary,
            emoji=emoji,
            custom_id="open_support_select"
        )
        self.categorias = categorias
    
    async def callback(self, interaction: disnake.Interaction):
        """Abre o select menu de categorias"""
        try:
            # Criar view temporária com select menu
            view = ui.View(timeout=60)
            select = SupportCategorySelect(self.categorias)
            view.add_item(select)
            
            await interaction.response.send_message(
                "📋 **Selecione o tipo de atendimento:**",
                view=view,
                ephemeral=True
            )
            
        except Exception as e:
            print(f"❌ Erro ao abrir select: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ Erro ao abrir menu. Tente novamente.",
                ephemeral=True
            )

class MultiSupportTicketView(ui.View):
    """View com botão que abre select menu de categorias"""
    
    def __init__(self, botoes_config: list, label_botao: str = "Abrir Ticket", emoji_botao: str = "🎫"):
        super().__init__(timeout=None)
        
        # Adicionar botão único que abre select menu
        botao = SupportSelectButton(label_botao, emoji_botao, botoes_config)
        self.add_item(botao)

class SupportTicketView(ui.View):
    """View persistente com botão de criar ticket de suporte"""
    
    def __init__(self, nome_botao="Abrir Ticket de Suporte"):
        super().__init__(timeout=None)
        self.add_item(SupportTicketButton(nome_botao))

class GeneratePaymentButton(ui.Button):
    """Botão para gerar pagamento no ticket"""
    
    def __init__(self):
        super().__init__(
            label="Gerar Pagamento",
            style=disnake.ButtonStyle.success,
            emoji="💳",
            custom_id="generate_payment_button"
        )
    
    async def callback(self, interaction: disnake.Interaction):
        """Callback para gerar pagamento"""
        try:
            # Verificar se é canal de ticket
            if not interaction.channel.name.startswith('ticket-'):
                await interaction.response.send_message(
                    "❌ Este comando só funciona em canais de ticket.",
                    ephemeral=True
                )
                return
            
            # Buscar dados do ticket
            import bot
            ticket_data = bot.active_tickets.get(interaction.user.id)
            
            if not ticket_data or not ticket_data.get('product_id'):
                await interaction.response.send_message(
                    "❌ Não foi possível identificar o produto do ticket.",
                    ephemeral=True
                )
                return
            
            # Mostrar mensagem de loading
            await interaction.response.send_message(
                "⏳ **Gerando pagamento...**\n"
                "Por favor, aguarde alguns segundos.",
                ephemeral=False
            )
            
            # Buscar produto
            from models.product_model import ProductModel
            product_model = ProductModel()
            product = await product_model.get_product_by_id(
                ticket_data['product_id'], 
                interaction.guild_id
            )
            
            if not product:
                await interaction.channel.send("❌ Produto não encontrado!")
                return
            
            # Gerar pagamento
            from utils.payment_utils import PaymentUtils
            from models.transaction_model import TransactionModel
            
            transaction_model = TransactionModel()
            
            # Criar transação
            transaction = await transaction_model.create_transaction(
                user_id=interaction.user.id,
                product_id=product['id'],
                amount=product['price'],
                status='pending',
                delivery_channel_id=interaction.channel.id,
                guild_id=interaction.guild_id
            )
            
            if not transaction:
                await interaction.channel.send("❌ Erro ao criar transação!")
                return
            
            # Gerar Pix
            payment_utils = PaymentUtils()
            payment_data = await payment_utils.create_pix_payment(
                amount=product['price'],
                description=f"Compra: {product['name']}",
                customer_email=f"{interaction.user.name.lower().replace(' ', '')}@khaos.com",
                customer_name=interaction.user.display_name
            )
            
            if payment_data:
                # Atualizar transação
                await transaction_model.update_transaction(transaction['id'], {
                    'payment_id': payment_data.get('id'),
                    'pix_code': payment_data.get('pix_code'),
                    'qr_code': payment_data.get('qr_code'),
                    'email': f"{interaction.user.name.lower().replace(' ', '')}@khaos.com"
                })
                
                # Enviar pagamento
                embed = disnake.Embed(
                    title="✅ Pagamento Gerado!",
                    description=f"**Produto:** {product['name']}\n**Valor:** R$ {product['price']:.2f}",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="📱 QR Code",
                    value="Escaneie o QR Code abaixo com seu app de pagamento:",
                    inline=False
                )
                
                embed.add_field(
                    name="🔢 Código Pix",
                    value=f"```{payment_data.get('pix_code', 'N/A')}```",
                    inline=False
                )
                
                embed.add_field(
                    name="⏰ Validade",
                    value="⏱️ **30 minutos** para efetuar o pagamento",
                    inline=False
                )
                
                embed.set_footer(text=f"ID: {transaction['id']} • Use /status para verificar")
                
                await interaction.channel.send(embed=embed)
                
                # Gerar QR Code
                try:
                    import qrcode
                    import io
                    
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4
                    )
                    qr.add_data(payment_data['qr_code'])
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    await interaction.channel.send(
                        content=f"{interaction.user.mention} 📱 **Seu QR Code Pix:**",
                        file=disnake.File(img_buffer, filename='qrcode_pix.png')
                    )
                except Exception as qr_error:
                    print(f"Erro ao gerar QR Code: {qr_error}")
            else:
                await interaction.channel.send("❌ Erro ao gerar pagamento Pix!")
                
        except Exception as e:
            print(f"Erro ao gerar pagamento pelo botão: {e}")
            import traceback
            traceback.print_exc()
            await interaction.channel.send("❌ Erro ao processar pagamento. Tente novamente.")

class TicketChannelView(ui.View):
    """View para canais de ticket com botões"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GeneratePaymentButton())
        self.add_item(CloseTicketButton())
# Force redeploy - fix InputText default to value
# Force deploy - 10/24/2025 16:37:09
