# py-cord: Usa ui.InputText (não ui.TextInput)
import discord
from discord import ui
from typing import List, Dict, Optional
from models.product_model import ProductModel
from utils.ticket_manager import TicketManager
import asyncio
import time

# Sistema de aguardar input do usuário (substitui modais)
waiting_for_input = {}
# Formato: {user_id: {'type': str, 'guild_id': int, 'channel_id': int, 'extra_data': dict}}

async def process_user_input(message: discord.Message, input_data: dict):
    """Processa input do usuário baseado no tipo aguardado"""
    try:
        input_type = input_data['type']
        guild_id = input_data['guild_id']
        user_content = message.content.strip()
        
        print(f"🔧 Processando input tipo '{input_type}' de {message.author.name}: {user_content[:50]}...")
        
        # Buscar view ativa para esta guild
        view = active_config_views.get(guild_id)
        if not view:
            await message.channel.send(
                f"{message.author.mention} ❌ Sessão de configuração expirada. Use `/setup_ticket` novamente.",
                delete_after=10
            )
            return
        
        # Processar baseado no tipo
        if input_type == 'title':
            view.config['title'] = user_content
            
        elif input_type == 'description':
            view.config['description'] = user_content
            
        elif input_type == 'color':
            # Converter cor hex para int
            try:
                color_hex = user_content.lower()
                if color_hex.startswith('#'):
                    color_hex = color_hex[1:]
                elif color_hex.startswith('0x'):
                    color_hex = color_hex[2:]
                
                if len(color_hex) == 3:
                    color_hex = color_hex[0]*2 + color_hex[1]*2 + color_hex[2]*2
                
                view.config['color'] = int(color_hex, 16)
            except (ValueError, IndexError):
                await message.channel.send(
                    f"{message.author.mention} ❌ Cor inválida! Use formato hex (#0099ff ou 0099ff)",
                    delete_after=10
                )
                return
                
        elif input_type == 'author':
            view.config['author'] = user_content if user_content else None
            
        elif input_type == 'fields':
            # Parse campos (Nome|Valor|inline por linha)
            fields = []
            if user_content:
                for line in user_content.split('\n'):
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
            view.config['fields'] = fields
            
        elif input_type == 'images':
            # Parse URLs (linha 1 = imagem, linha 2 = thumbnail)
            lines = user_content.split('\n')
            view.config['image'] = lines[0].strip() if len(lines) > 0 and lines[0].strip() else None
            view.config['thumbnail'] = lines[1].strip() if len(lines) > 1 and lines[1].strip() else None
            
        elif input_type == 'footer':
            view.config['footer'] = user_content if user_content else None
            
        elif input_type == 'button_name':
            view.config['button_name'] = user_content
            
        elif input_type == 'product_filter':
            # Parse IDs (1,2,3 ou vazio para todos)
            if user_content:
                try:
                    product_ids = [int(x.strip()) for x in user_content.split(',')]
                    view.config['product_ids'] = product_ids
                except ValueError:
                    await message.channel.send(
                        f"{message.author.mention} ❌ IDs inválidos! Use números separados por vírgula (1,2,3)",
                        delete_after=10
                    )
                    return
            else:
                view.config['product_ids'] = None
        
        # Atualizar preview
        if view.message:
            await view.message.edit(embed=view._create_embed(), view=view)
            print(f"✅ Preview atualizado com sucesso para {input_type}")
        
        # Feedback ao usuário
        await message.add_reaction("✅")
        
    except Exception as e:
        print(f"❌ Erro ao processar input: {e}")
        import traceback
        traceback.print_exc()
        await message.channel.send(
            f"{message.author.mention} ❌ Erro ao processar: {str(e)[:100]}",
            delete_after=10
        )

class SetupMessageModal(ui.Modal):
    """Modal para criar mensagens embed personalizadas sem botões"""
    
    def __init__(self):
        super().__init__(title="Criar Mensagem Embed")
        
        self.add_item(ui.InputText(
            label="Título", 
            placeholder="Ex: Bem-vindo ao Servidor!", 
            value="",
            max_length=256,
            required=False
        ))
        
        self.add_item(ui.InputText(
            label="Descrição", 
            placeholder="Escreva o conteúdo principal da mensagem...", 
            value="",
            style=discord.InputTextStyle.paragraph,
            max_length=4000,
            required=True
        ))
        
        self.add_item(ui.InputText(
            label="URL da Imagem", 
            placeholder="Cole o link da imagem (opcional)", 
            value="",
            required=False,
            max_length=500
        ))
        
        self.add_item(ui.InputText(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #0099ff ou 0x0099ff", 
            value="#0099ff",
            max_length=10
        ))
        
        self.add_item(ui.InputText(
            label="Rodapé (Footer)", 
            placeholder="Texto no rodapé (opcional)", 
            value="",
            required=False,
            max_length=100
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a criação da mensagem embed"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            import time
            start_time = time.time()
            
            # Acessar valores via children
            titulo = self.children[0].value.strip()
            descricao = self.children[1].value.strip()
            url_imagem = self.children[2].value.strip()
            cor_hex = self.children[3].value.strip()
            rodape = self.children[4].value.strip()
            
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
            embed = discord.Embed(description=descricao, color=cor_int)
            if titulo:
                embed.title = titulo
            if url_imagem and url_imagem.startswith(('http://', 'https://')):
                embed.set_image(url=url_imagem)
            if rodape:
                embed.set_footer(text=rodape)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            print(f"⏱️ SetupMessageModal processado em {time.time() - start_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao criar mensagem embed: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro: {str(e)[:100]}", ephemeral=True)

# Sistema de gerenciamento de views ativas
active_config_views = {}

class TicketConfigView(ui.View):
    """View interativa para configurar tickets com preview em tempo real"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=1800)  # 30 minutos
        self.guild_id = guild_id
        self.config = {
            'title': "🛒 Sistema de Vendas Automatizado",
            'description': "Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            'color': 0x0099ff,
            'button_name': "Criar Ticket de Compra",
            'product_ids': None,
            'author': None,
            'thumbnail': None,
            'image': None,
            'footer': "Atendimento 24/7 • Pagamento via Pix",
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
        self.add_item(ProductFilterButton())
        self.add_item(PreviewButton())
        self.add_item(FinishButton())
    
    async def on_timeout(self):
        """Quando o timeout expira"""
        if self.guild_id in active_config_views:
            del active_config_views[self.guild_id]
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)
    
    async def update_preview(self, interaction: discord.Interaction):
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
        embed = discord.Embed(
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
        
        # Adicionar informações sobre filtro de produtos
        if self.config['product_ids']:
            embed.add_field(
                name="🔍 Produtos Filtrados",
                value=f"Apenas os produtos com IDs: **{', '.join(map(str, self.config['product_ids']))}** aparecerão neste ticket.",
                inline=False
            )
        
        return embed

    async def finish_configuration(self, interaction: discord.Interaction):
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
            embed = discord.Embed(
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
            
            # Adicionar informações sobre filtro de produtos
            if self.config['product_ids']:
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

class TitleButton(ui.Button):
    """Botão para editar título"""
    
    def __init__(self):
        super().__init__(
            label="Título",
            style=discord.ButtonStyle.secondary,
            emoji="📝",
            custom_id="edit_title"
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Registrar que usuário está aguardando input
        waiting_for_input[interaction.user.id] = {
            'type': 'title',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "📝 **Digite o novo título do embed:**\n"
            "Digite sua resposta no chat abaixo. A mensagem será processada automaticamente.\n\n"
            "**Exemplo:** `🛒 Sistema de Vendas Automatizado`",
            ephemeral=True,
            delete_after=60
        )

class DescriptionButton(ui.Button):
    """Botão para editar descrição"""
    
    def __init__(self):
        super().__init__(
            label="Descrição",
            style=discord.ButtonStyle.secondary,
            emoji="📄",
            custom_id="edit_description"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'description',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "📄 **Digite a nova descrição do embed:**\n"
            "Digite sua resposta no chat. Pode ser texto longo.\n\n"
            "**Exemplo:** `Clique no botão abaixo para criar um ticket e ser atendido!`",
            ephemeral=True,
            delete_after=60
        )

class ColorButton(ui.Button):
    """Botão para editar cor"""
    
    def __init__(self):
        super().__init__(
            label="Cor",
            style=discord.ButtonStyle.secondary,
            emoji="🎨",
            custom_id="edit_color"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'color',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "🎨 **Digite a cor do embed (formato hex):**\n"
            "Digite no chat. Formatos aceitos: `#0099ff`, `0099ff` ou `09f`\n\n"
            "**Exemplo:** `#FF5733`",
            ephemeral=True,
            delete_after=60
        )

class AuthorButton(ui.Button):
    """Botão para editar autor"""
    
    def __init__(self):
        super().__init__(
            label="Autor",
            style=discord.ButtonStyle.secondary,
            emoji="👤",
            custom_id="edit_author"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'author',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "👤 **Digite o nome do autor (opcional):**\n"
            "Digite no chat. Deixe vazio para remover.\n\n"
            "**Exemplo:** `Sistema de Vendas` ou `vazio` para remover",
            ephemeral=True,
            delete_after=60
        )

class FieldsButton(ui.Button):
    """Botão para editar campos"""
    
    def __init__(self):
        super().__init__(
            label="Campos",
            style=discord.ButtonStyle.secondary,
            emoji="📋",
            custom_id="edit_fields"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'fields',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "📋 **Digite os campos do embed (um por linha):**\n"
            "Formato: `Nome|Valor|inline` (inline = true ou false)\n\n"
            "**Exemplo:**\n"
            "`Horário|24/7|true`\n"
            "`Pagamento|PIX|true`",
            ephemeral=True,
            delete_after=60
        )

class ImageButton(ui.Button):
    """Botão para editar imagens"""
    
    def __init__(self):
        super().__init__(
            label="Imagens",
            style=discord.ButtonStyle.secondary,
            emoji="🖼️",
            custom_id="edit_images"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'images',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "🖼️ **Digite as URLs das imagens:**\n"
            "Linha 1: URL da imagem principal\n"
            "Linha 2: URL da thumbnail (opcional)\n\n"
            "**Exemplo:**\n"
            "`https://exemplo.com/banner.png`\n"
            "`https://exemplo.com/thumb.png`",
            ephemeral=True,
            delete_after=60
        )

class FooterButton(ui.Button):
    """Botão para editar rodapé"""
    
    def __init__(self):
        super().__init__(
            label="Rodapé",
            style=discord.ButtonStyle.secondary,
            emoji="🏷️",
            custom_id="edit_footer"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'footer',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "📌 **Digite o texto do rodapé (opcional):**\n"
            "Digite no chat. Deixe vazio para remover.\n\n"
            "**Exemplo:** `Atendimento 24/7 • Pagamento via Pix`",
            ephemeral=True,
            delete_after=60
        )

class ButtonNameButton(ui.Button):
    """Botão para editar nome do botão"""
    
    def __init__(self):
        super().__init__(
            label="Botão",
            style=discord.ButtonStyle.secondary,
            emoji="🔘",
            custom_id="edit_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'button_name',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "🔘 **Digite o nome do botão de criar ticket:**\n"
            "Digite no chat.\n\n"
            "**Exemplo:** `Criar Ticket de Compra` ou `Comprar Agora`",
            ephemeral=True,
            delete_after=60
        )

class ProductFilterButton(ui.Button):
    """Botão para editar filtro de produtos"""
    
    def __init__(self):
        super().__init__(
            label="Produtos",
            style=discord.ButtonStyle.secondary,
            emoji="🛍️",
            custom_id="edit_products"
        )
    
    async def callback(self, interaction: discord.Interaction):
        waiting_for_input[interaction.user.id] = {
            'type': 'product_filter',
            'guild_id': interaction.guild_id,
            'channel_id': interaction.channel_id
        }
        
        await interaction.response.send_message(
            "🔍 **Digite os IDs dos produtos permitidos (opcional):**\n"
            "Formato: números separados por vírgula\n"
            "Deixe vazio para permitir todos os produtos.\n\n"
            "**Exemplo:** `1,2,3,5` ou `vazio` para todos",
            ephemeral=True,
            delete_after=60
        )

class PreviewButton(ui.Button):
    """Botão para atualizar preview"""
    
    def __init__(self):
        super().__init__(
            label="Preview",
            style=discord.ButtonStyle.primary,
            emoji="👁️",
            custom_id="update_preview"
        )
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await view.update_preview(interaction)

class FinishButton(ui.Button):
    """Botão para finalizar configuração"""
    
    def __init__(self):
        super().__init__(
            label="Finalizar",
            style=discord.ButtonStyle.success,
            emoji="✅",
            custom_id="finish_config"
        )
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await view.finish_configuration(interaction)

# MODAIS DELETADOS - Sistema "aguardar mensagem" já implementado
# TitleModal, DescriptionModal, ColorModal, AuthorModal, FieldsModal, 
# ImageModal, FooterModal, ButtonNameModal, ProductFilterModal

class SetupTicketModal(ui.Modal):
    """Modal para configurar o sistema de tickets"""
    
    def __init__(self):
        super().__init__(title="Configurar Sistema de Tickets")
        
        self.add_item(ui.InputText(
            label="Headline", 
            placeholder="Ex: Sistema de Vendas Automatizado", 
            value="🛒 Sistema de Vendas Automatizado",
            max_length=100
        ))
        
        self.add_item(ui.InputText(
            label="Descrição", 
            placeholder="Ex: Clique no botão abaixo para criar um ticket de compra", 
            value="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            style=discord.InputTextStyle.paragraph,
            max_length=1000
        ))
        
        self.add_item(ui.InputText(
            label="IDs dos Produtos (vazio = todos)", 
            placeholder="Ex: 1,2,3,5 ou deixe vazio para todos", 
            value="",
            required=False,
            max_length=200
        ))
        
        self.add_item(ui.InputText(
            label="Nome do Botão", 
            placeholder="Ex: Criar Ticket de Compra", 
            value="Criar Ticket de Compra",
            max_length=80
        ))
        
        self.add_item(ui.InputText(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #0099ff ou 0x0099ff", 
            value="#0099ff",
            max_length=10
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a configuração do sistema de tickets"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            import time
            import asyncio
            from models.guild_config_model import GuildConfigModel
            
            start_time = time.time()
            
            # Acessar valores via children
            headline = self.children[0].value
            descricao = self.children[1].value
            product_ids_input = self.children[2].value.strip()
            nome_botao = self.children[3].value
            cor_hex = self.children[4].value.strip()
            
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
            success = await asyncio.wait_for(
                guild_config.set_ticket_product_filter(
                    guild_id=interaction.guild_id,
                    product_ids=allowed_product_ids
                ),
                timeout=10.0
            )
            
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
            embed = discord.Embed(title=headline, description=descricao, color=cor_int)
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
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
            print(f"⏱️ SetupTicketModal processado em {time.time() - start_time:.2f}s")

        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Operação demorou muito. Tente novamente.", ephemeral=True)
        except Exception as e:
            print(f"❌ Erro ao configurar sistema de tickets: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro: {str(e)[:100]}", ephemeral=True)

class CouponInputModal(ui.Modal):
    """Modal para coletar código de cupom (opcional)"""
    
    def __init__(self, user, guild, product):
        super().__init__(title="Cupom de Desconto (Opcional)")
        self.user = user
        self.guild = guild
        self.product = product
        
        self.coupon_code = ui.InputText(
            label="Código do Cupom",
            placeholder="Digite o código do cupom ou deixe em branco",
            required=False,
            max_length=50
        )
        
        self.add_item(self.coupon_code)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa o cupom e cria o ticket"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            start_time = time.time()
            
            # Acessar valor via atributo
            coupon_code = self.coupon_code.value.strip() if self.coupon_code.value else None
            
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
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
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
    
    def __init__(self, products: List[Dict], options: List[discord.SelectOption]):
        super().__init__(
            placeholder="Escolha um produto...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.products = products
    
    async def callback(self, interaction: discord.Interaction):
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
            except discord.errors.NotFound:
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
            option = discord.SelectOption(
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

class CreateCouponModal(ui.Modal):
    """Modal para criar cupom"""
    
    def __init__(self):
        super().__init__(title="Criar Novo Cupom")
        
        self.add_item(ui.InputText(
            label="Código do Cupom",
            placeholder="Ex: PRIMEIRACOMPRA",
            max_length=50,
            required=True
        ))
        
        self.add_item(ui.InputText(
            label="Desconto (%)",
            placeholder="Ex: 10 para 10%",
            max_length=5,
            required=True
        ))
        
        self.add_item(ui.InputText(
            label="Limite de Usos (0 = ilimitado)",
            placeholder="Ex: 100",
            value="0",
            max_length=10,
            required=False
        ))
        
        self.add_item(ui.InputText(
            label="Um uso por usuário? (sim/nao)",
            placeholder="sim ou nao",
            value="nao",
            max_length=3,
            required=False
        ))
        
        self.add_item(ui.InputText(
            label="Data Expiração (DD/MM/YYYY ou vazio)",
            placeholder="31/12/2025",
            required=False,
            max_length=10
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa criação do cupom"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from models.coupon_model import CouponModel
            from datetime import datetime
            import asyncio
            import time
            
            start_time = time.time()
            
            # Acessar valores via children
            code = self.children[0].value.upper().strip()
            discount = float(self.children[1].value.strip())
            max_uses_str = self.children[2].value.strip()
            max_uses = int(max_uses_str) if max_uses_str and max_uses_str != "0" else None
            one_per_user = self.children[3].value.strip().lower() == "sim"
            expires_str = self.children[4].value.strip()
            
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
                embed = discord.Embed(
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
        super().__init__(title="Configurar Tickets de Suporte")
        
        self.add_item(ui.InputText(
            label="Título da Mensagem", 
            placeholder="Ex: Central de Atendimento", 
            value="🎫 Central de Atendimento",
            max_length=100
        ))
        
        self.add_item(ui.InputText(
            label="Descrição da Mensagem", 
            placeholder="Ex: Clique no botão abaixo para abrir um ticket", 
            value="Clique no botão abaixo e selecione o tipo de atendimento que você precisa.",
            max_length=1000
        ))
        
        self.add_item(ui.InputText(
            label="Opções Menu (EMOJI|Nome|Descrição)", 
            placeholder="Uma por linha", 
            value="❤️|Parcerias|Para os interessados em colaborar conosco.\n💡|Dúvidas|Caso esteja com dúvidas em algo, abra um ticket.\n✅|Denúncias|Realize denúncias através desse ticket.\n🎁|Sorteios|Aqui você poderá resgatar sua premiação de sorteios.",
            style=discord.InputTextStyle.paragraph,
            max_length=1000,
            required=True
        ))
        
        self.add_item(ui.InputText(
            label="Nome do Botão | Emoji (opcional)", 
            placeholder="Ex: Abrir Ticket | 🎫", 
            value="Abrir Ticket | 🎫",
            max_length=100
        ))
        
        self.add_item(ui.InputText(
            label="Cor do Embed (Hex)", 
            placeholder="Ex: #5865F2", 
            value="#5865F2",
            max_length=10
        ))

    async def on_submit(self, interaction: discord.Interaction):
        """Processa a configuração do sistema de tickets de suporte"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            import time
            start_time = time.time()
            
            # Acessar valores via children
            titulo = self.children[0].value.strip()
            descricao = self.children[1].value.strip()
            opcoes_text = self.children[2].value.strip()
            botao_config = self.children[3].value.strip()
            cor_hex = self.children[4].value.strip()
            
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
            embed = discord.Embed(title=titulo, description=descricao if descricao else None, color=cor_int)
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
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"support_ticket_{nome.lower().replace(' ', '_')}"
        )
        self.categoria = categoria
        self.nome_ticket = nome
    
    async def callback(self, interaction: discord.Interaction):
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
            style=discord.ButtonStyle.danger,
            emoji="🆘",
            custom_id="create_support_ticket_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
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
            options.append(discord.SelectOption(
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
    
    async def callback(self, interaction: discord.Interaction):
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
            style=discord.ButtonStyle.primary,
            emoji=emoji,
            custom_id="open_support_select"
        )
        self.categorias = categorias
    
    async def callback(self, interaction: discord.Interaction):
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
            style=discord.ButtonStyle.success,
            emoji="💳",
            custom_id="generate_payment_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
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
                embed = discord.Embed(
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
                        file=discord.File(img_buffer, filename='qrcode_pix.png')
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
