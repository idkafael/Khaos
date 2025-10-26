# py-cord: Usa ui.InputText (não ui.TextInput)
import discord
from discord import ui
from typing import List, Dict, Optional
from models.product_model import ProductModel
from utils.ticket_manager import TicketManager
import asyncio

class SetupMessageModal(ui.Modal):
    """Modal para criar mensagens embed personalizadas sem botões"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            title="Criar Mensagem Embed", 
            timeout=600,
            custom_id="modal_setup_message"
        )
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
        print(f"🔧 MODAL SUBMIT: SetupMessageModal iniciado por {interaction.user.name}")
        
        try:
            # Verificar se interaction ainda é válida
            if interaction.response.is_done():
                print("❌ Interaction já foi respondida!")
                return
                
            print(f"Modal de mensagem submetido por {interaction.user.name}")
            titulo = self.children[0].value.strip()
            descricao = self.children[1].value.strip()
            url_imagem = self.children[2].value.strip()
            cor_hex = self.children[3].value.strip()
            rodape = self.children[4].value.strip()
            
            print(f"Valores: titulo={titulo}, descricao={descricao[:50]}..., cor={cor_hex}")
            
            # Converter cor hex para int
            try:
                cor_hex = cor_hex.strip().lower()
                
                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]
                
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                
                cor_int = int(cor_hex, 16)
                print(f"Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0x0099ff
            
            # Criar embed
            embed = discord.Embed(
                description=descricao,
                color=cor_int
            )
            
            # Adicionar título se fornecido
            if titulo:
                embed.title = titulo
            
            # Adicionar imagem se fornecida
            if url_imagem and url_imagem.startswith(('http://', 'https://')):
                try:
                    embed.set_image(url=url_imagem)
                    print(f"Imagem adicionada: {url_imagem}")
                except Exception as e:
                    print(f"Erro ao adicionar imagem: {e}")
            
            # Adicionar rodapé se fornecido
            if rodape:
                embed.set_footer(text=rodape)
            
            # Enviar mensagem embed (sem view/botões)
            print("🔧 Enviando resposta do modal...")
            await interaction.response.send_message(embed=embed)
            print("✅ Mensagem embed criada com sucesso")
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao criar mensagem embed: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar enviar mensagem de erro
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Erro ao criar mensagem embed.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erro ao criar mensagem embed.", ephemeral=True)
            except Exception as e2:
                print(f"❌ Falha ao enviar mensagem de erro: {e2}")
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL SetupMessageModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

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
        modal = TitleModal()
        await interaction.response.send_modal(modal)

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
        modal = DescriptionModal()
        await interaction.response.send_modal(modal)

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
        modal = ColorModal()
        await interaction.response.send_modal(modal)

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
        modal = AuthorModal()
        await interaction.response.send_modal(modal)

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
        modal = FieldsModal()
        await interaction.response.send_modal(modal)

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
        modal = ImageModal()
        await interaction.response.send_modal(modal)

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
        modal = FooterModal()
        await interaction.response.send_modal(modal)

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
        modal = ButtonNameModal()
        await interaction.response.send_modal(modal)

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
        modal = ProductFilterModal()
        await interaction.response.send_modal(modal)

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

class TitleModal(ui.Modal):
    """Modal para editar título"""
    
    def __init__(self):
        super().__init__(
            title="Editar Título", 
            timeout=600,
            custom_id="modal_edit_title"
        )
        self.add_item(ui.InputText(
            label="Título do Embed",
            placeholder="Ex: Sistema de Vendas Automatizado",
            value="🛒 Sistema de Vendas Automatizado",
            max_length=256,
            required=True
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        print(f"🔧 MODAL SUBMIT: TitleModal por {interaction.user.name}")
        try:
            # Verificar se interaction ainda é válida
            if interaction.response.is_done():
                print("❌ Interaction já foi respondida!")
                return
                
            title = self.children[0].value.strip()
            print(f"🔧 Título recebido: {title}")
            
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['title'] = title
                print(f"🔧 View encontrada, atualizando preview...")
                await view.update_preview(interaction)
                print("✅ Preview atualizado com sucesso")
            else:
                print(f"❌ View não encontrada para guild {interaction.guild_id}")
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"❌ Erro ao editar título: {e}")
            import traceback
            traceback.print_exc()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Erro ao editar título.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erro ao editar título.", ephemeral=True)
            except Exception as e2:
                print(f"❌ Erro ao enviar mensagem de erro: {e2}")
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        """Handler de erros do modal"""
        print(f"❌ ERRO NO MODAL TitleModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class DescriptionModal(ui.Modal):
    """Modal para editar descrição"""
    
    def __init__(self):
        super().__init__(
            title="Editar Descrição", 
            timeout=600,
            custom_id="modal_edit_description"
        )
        self.add_item(ui.InputText(
            label="Descrição do Embed",
            placeholder="Ex: Clique no botão abaixo para criar um ticket de compra",
            value="Clique no botão abaixo para criar um ticket de compra e ser atendido por nosso bot!",
            style=discord.InputTextStyle.paragraph,
            max_length=4000,
            required=True
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            description = self.children[0].value.strip()
            
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['description'] = description
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar descrição: {e}")
            await interaction.response.send_message("❌ Erro ao editar descrição.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        """Handler de erros do modal"""
        print(f"❌ ERRO NO MODAL DescriptionModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class ColorModal(ui.Modal):
    """Modal para editar cor"""
    
    def __init__(self):
        super().__init__(
            title="Editar Cor", 
            timeout=600,
            custom_id="modal_edit_color"
        )
        self.add_item(ui.InputText(
            label="Cor do Embed (Hex)",
            placeholder="Ex: #0099ff ou 0x0099ff",
            value="#0099ff",
            max_length=10,
            required=True
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            color_hex = self.children[0].value.strip()
            
            # Converter cor hex para int
            try:
                color_hex = color_hex.strip().lower()
                
                if color_hex.startswith('#'):
                    color_hex = color_hex[1:]
                elif color_hex.startswith('0x'):
                    color_hex = color_hex[2:]
                
                if len(color_hex) == 3:
                    color_hex = color_hex[0] + color_hex[0] + color_hex[1] + color_hex[1] + color_hex[2] + color_hex[2]
                
                color_int = int(color_hex, 16)
            except (ValueError, IndexError):
                color_int = 0x0099ff
            
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['color'] = color_int
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar cor: {e}")
            await interaction.response.send_message("❌ Erro ao editar cor.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL ColorModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class AuthorModal(ui.Modal):
    """Modal para editar autor"""
    
    def __init__(self):
        super().__init__(
            title="Editar Autor", 
            timeout=600,
            custom_id="modal_edit_author"
        )
        self.add_item(ui.InputText(
            label="Nome do Autor",
            placeholder="Ex: Sistema de Vendas",
            value="",
            max_length=256,
            required=False
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            author = self.children[0].value.strip() if self.children[0].value else None
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['author'] = author
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar autor: {e}")
            await interaction.response.send_message("❌ Erro ao editar autor.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL AuthorModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class FieldsModal(ui.Modal):
    """Modal para editar campos"""
    
    def __init__(self):
        super().__init__(
            title="Editar Campos", 
            timeout=600,
            custom_id="modal_edit_fields"
        )
        self.add_item(ui.InputText(
            label="Campos (Nome|Valor|Inline)",
            placeholder="Um campo por linha. Ex: Nome|Valor|true",
            value="",
            style=discord.InputTextStyle.paragraph,
            max_length=4000,
            required=False
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            fields_text = self.children[0].value.strip()
            fields = []
            
            if fields_text:
                for line in fields_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split('|')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        value = parts[1].strip()
                        inline = parts[2].strip().lower() == 'true' if len(parts) > 2 else False
                        
                        fields.append({
                            'name': name,
                            'value': value,
                            'inline': inline
                        })
            
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['fields'] = fields
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar campos: {e}")
            await interaction.response.send_message("❌ Erro ao editar campos.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL FieldsModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class ImageModal(ui.Modal):
    """Modal para editar imagens"""
    
    def __init__(self):
        super().__init__(
            title="Editar Imagens", 
            timeout=600,
            custom_id="modal_edit_images"
        )
        self.add_item(ui.InputText(
            label="URL da Imagem Principal",
            placeholder="https://exemplo.com/imagem.png",
            value="",
            max_length=500,
            required=False
        ))
        self.add_item(ui.InputText(
            label="URL da Thumbnail",
            placeholder="https://exemplo.com/thumbnail.png",
            value="",
            max_length=500,
            required=False
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            image_url = self.children[0].value.strip() if self.children[0].value else None
            thumbnail_url = self.children[1].value.strip() if self.children[1].value else None
            
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['image'] = image_url
                view.config['thumbnail'] = thumbnail_url
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar imagens: {e}")
            await interaction.response.send_message("❌ Erro ao editar imagens.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL ImageModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class FooterModal(ui.Modal):
    """Modal para editar rodapé"""
    
    def __init__(self):
        super().__init__(
            title="Editar Rodapé", 
            timeout=600,
            custom_id="modal_edit_footer"
        )
        self.add_item(ui.InputText(
            label="Texto do Rodapé",
            placeholder="Ex: Atendimento 24/7 • Pagamento via Pix",
            value="Atendimento 24/7 • Pagamento via Pix",
            max_length=2048,
            required=False
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            footer = self.children[0].value.strip() if self.children[0].value else None
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['footer'] = footer
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar rodapé: {e}")
            await interaction.response.send_message("❌ Erro ao editar rodapé.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL FooterModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class ButtonNameModal(ui.Modal):
    """Modal para editar nome do botão"""
    
    def __init__(self):
        super().__init__(
            title="Editar Nome do Botão", 
            timeout=600,
            custom_id="modal_edit_button_name"
        )
        self.add_item(ui.InputText(
            label="Nome do Botão",
            placeholder="Ex: Criar Ticket de Compra",
            value="Criar Ticket de Compra",
            max_length=80,
            required=True
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            button_name = self.children[0].value.strip()
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['button_name'] = button_name
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar nome do botão: {e}")
            await interaction.response.send_message("❌ Erro ao editar nome do botão.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL ButtonNameModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class ProductFilterModal(ui.Modal):
    """Modal para editar filtro de produtos"""
    
    def __init__(self):
        super().__init__(
            title="Editar Filtro de Produtos", 
            timeout=600,
            custom_id="modal_edit_product_filter"
        )
        self.add_item(ui.InputText(
            label="IDs dos Produtos (vazio = todos)",
            placeholder="Ex: 1,2,3,5 ou deixe vazio para todos",
            value="",
            max_length=200,
            required=False
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            product_ids_input = self.children[0].value.strip()
            product_ids = None
            
            if product_ids_input:
                try:
                    product_ids = [int(pid.strip()) for pid in product_ids_input.split(',') if pid.strip()]
                except ValueError:
                    await interaction.response.send_message("❌ IDs de produtos inválidos! Use números separados por vírgula.", ephemeral=True)
                    return
            
            # Buscar a view ativa
            view = active_config_views.get(interaction.guild_id)
            if view:
                view.config['product_ids'] = product_ids
                await view.update_preview(interaction)
            else:
                await interaction.response.send_message("❌ Sessão de configuração expirada. Use /setup_ticket novamente.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao editar filtro de produtos: {e}")
            await interaction.response.send_message("❌ Erro ao editar filtro de produtos.", ephemeral=True)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL ProductFilterModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class SetupTicketModal(ui.Modal):
    """Modal para configurar o sistema de tickets"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Configurar Sistema de Tickets", timeout=600)
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
        print(f"🔧 MODAL SUBMIT: SetupTicketModal iniciado por {interaction.user.name}")
        
        try:
            # Verificar se interaction ainda é válida
            if interaction.response.is_done():
                print("❌ Interaction já foi respondida!")
                return
                
            print("🔧 ========== SETUP TICKET MODAL DEBUG ==========")
            print(f"🔧 Modal submetido por {interaction.user.name} (ID: {interaction.user.id})")
            print(f"🔧 Guild: {interaction.guild.name} (ID: {interaction.guild_id})")
            print(f"🔧 Channel: {interaction.channel.name} (ID: {interaction.channel_id})")
            print(f"🔧 Interaction type: {type(interaction)}")
            print(f"🔧 Interaction responded: {interaction.response.is_done()}")

            # Debug: Verificar todos os children
            print(f"🔧 Modal tem {len(self.children)} children:")
            for i, child in enumerate(self.children):
                print(f"🔧   Child {i}: {child.label} = '{child.value}' (type: {type(child.value)})")

            headline = self.children[0].value
            descricao = self.children[1].value
            product_ids_input = self.children[2].value.strip()
            nome_botao = self.children[3].value
            cor_hex = self.children[4].value.strip()

            print("🔧 ========== VALORES RECEBIDOS ==========")
            print(f"🔧 Headline: '{headline}' (type: {type(headline)})")
            print(f"🔧 Descrição: '{descricao}' (type: {type(descricao)})")
            print(f"🔧 Product IDs Input: '{product_ids_input}' (type: {type(product_ids_input)})")
            print(f"🔧 Nome Botão: '{nome_botao}' (type: {type(nome_botao)})")
            print(f"🔧 Cor Hex: '{cor_hex}' (type: {type(cor_hex)})")
            print(f"🔧 User permissions: {interaction.user.guild_permissions}")
            print(f"🔧 User is admin: {interaction.user.guild_permissions.administrator}")
            print(f"🔧 Bot has manage channels: {interaction.guild.me.guild_permissions.manage_channels}")
            print(f"🔧 Bot has manage roles: {interaction.guild.me.guild_permissions.manage_roles}")
            
            # Processar IDs dos produtos
            print("🔧 ========== PROCESSANDO PRODUTOS ==========")
            allowed_product_ids = None
            if product_ids_input:
                try:
                    # Converter string "1,2,3" para lista de inteiros
                    allowed_product_ids = [int(pid.strip()) for pid in product_ids_input.split(',') if pid.strip()]
                    print(f"✅ Produtos filtrados: {allowed_product_ids}")
                except ValueError as e:
                    print(f"❌ Erro ao converter IDs de produtos: {e}")
                    await interaction.response.send_message(
                        "❌ IDs de produtos inválidos! Use números separados por vírgula (ex: 1,2,3)",
                        ephemeral=True
                    )
                    return
            else:
                print("🔧 Nenhum filtro de produtos - todos produtos disponíveis")

            # Salvar configuração no banco de dados
            print("🔧 ========== SALVANDO NO BANCO ==========")
            from models.guild_config_model import GuildConfigModel
            guild_config = GuildConfigModel()

            print(f"🔧 GuildConfigModel inicializado: {guild_config}")
            print(f"🔧 Supabase URL: {guild_config.supabase._url}")
            print(f"🔧 Table name: {guild_config.table_name}")

            try:
                print(f"🔧 Tentando salvar filtro de produtos para guild {interaction.guild_id}")
                success = await guild_config.set_ticket_product_filter(
                    guild_id=interaction.guild_id,
                    product_ids=allowed_product_ids
                )
                print(f"🔧 Resultado do save: {success}")
            except Exception as e:
                print(f"❌ ERRO AO SALVAR NO BANCO: {e}")
                import traceback
                traceback.print_exc()

                # Verificar se é erro de coluna inexistente
                if "ticket_allowed_products" in str(e) or "column" in str(e).lower():
                    await interaction.response.send_message(
                        "❌ **Erro de configuração do banco de dados!**\n\n"
                        "A coluna `ticket_allowed_products` não existe na tabela.\n"
                        "Execute o arquivo `database_ticket_product_filter.sql` no Supabase.\n\n"
                        f"Erro técnico: {str(e)}",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f"❌ Erro interno do servidor. Verifique os logs.\n\nErro: {str(e)}",
                        ephemeral=True
                    )
                return
            
            print("🔧 ========== VERIFICANDO RESULTADO DO SAVE ==========")
            if success:
                if allowed_product_ids:
                    print(f"✅ Filtro de produtos salvo: {allowed_product_ids}")
                else:
                    print(f"✅ Filtro removido - todos produtos disponíveis")
            else:
                print(f"❌ FALHA AO SALVAR NO BANCO! Success = {success}")
                await interaction.response.send_message(
                    "❌ Erro ao salvar configuração no banco de dados. Verifique os logs.",
                    ephemeral=True
                )
                return

            # Converter cor hex para int
            print("🔧 ========== CONVERTENDO COR ==========")
            try:
                # Limpar a string de cor
                cor_hex_original = cor_hex
                cor_hex = cor_hex.strip().lower()

                print(f"🔧 Cor original: '{cor_hex_original}'")
                print(f"🔧 Cor após strip().lower(): '{cor_hex}'")

                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]  # Remove #
                    print(f"🔧 Removeu '#': '{cor_hex}'")
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]  # Remove 0x
                    print(f"🔧 Removeu '0x': '{cor_hex}'")

                # Garantir que tem 6 caracteres
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                    print(f"🔧 Expandiu cor de 3 para 6 chars: '{cor_hex}'")

                print(f"🔧 Convertendo '{cor_hex}' para int...")
                cor_int = int(cor_hex, 16)
                print(f"✅ Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"❌ Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0x0099ff  # Azul padrão

            # Criar embed com as configurações
            print("🔧 ========== CRIANDO EMBED ==========")
            try:
                embed = discord.Embed(
                    title=headline,
                    description=descricao,
                    color=cor_int
                )
                print(f"✅ Embed criado: title='{headline}', color={cor_int}")

                embed.add_field(
                    name="🚀 Como Funciona?",
                    value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
                    inline=False
                )
                print("✅ Field 'Como Funciona?' adicionado")

                # Adicionar info sobre filtro de produtos
                if allowed_product_ids:
                    embed.add_field(
                        name="🔍 Produtos Filtrados",
                        value=f"Apenas os produtos com IDs: **{', '.join(map(str, allowed_product_ids))}** aparecerão neste ticket.",
                        inline=False
                    )
                    print(f"✅ Field 'Produtos Filtrados' adicionado: {allowed_product_ids}")

                embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")
                print("✅ Footer adicionado")

                # Criar view com botão personalizado
                print("🔧 ========== CRIANDO VIEW ==========")
                view = TicketView(nome_botao)
                print(f"✅ View criada com botão: '{nome_botao}'")

                print("🔧 ========== ENVIANDO RESPOSTA ==========")
                print(f"🔧 Interaction responded: {interaction.response.is_done()}")

                try:
                    await interaction.response.send_message(embed=embed, view=view)
                    print("✅ Resposta enviada com sucesso!")
                    print("🎉 Modal processado completamente!")
                except Exception as e:
                    print(f"❌ ERRO AO ENVIAR RESPOSTA: {e}")
                    print(f"❌ Interaction already responded: {interaction.response.is_done()}")

                    # Se já foi respondido, tentar followup
                    if interaction.response.is_done():
                        print(f"🔧 Tentando followup message...")
                        try:
                            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                            print("✅ Followup enviado com sucesso!")
                        except Exception as e2:
                            print(f"❌ Erro no followup: {e2}")
                            # Última tentativa: editar a resposta original
                            try:
                                await interaction.edit_original_response(embed=embed, view=view)
                                print("✅ Edit original response com sucesso!")
                            except Exception as e3:
                                print(f"❌ Erro no edit original response: {e3}")
                                # Forçar erro para o usuário ver
                                raise e3
                    else:
                        raise e

            except Exception as e:
                print(f"❌ ERRO AO CRIAR EMBED/VIEW: {e}")
                import traceback
                traceback.print_exc()
                await interaction.response.send_message(
                    f"❌ Erro ao criar interface. Verifique os logs.\n\nErro: {str(e)}",
                    ephemeral=True
                )
                return
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao configurar sistema de tickets: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar enviar mensagem de erro
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Erro ao configurar sistema de tickets.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erro ao configurar sistema de tickets.", ephemeral=True)
            except Exception as e2:
                print(f"❌ Falha ao enviar mensagem de erro: {e2}")

class CouponInputModal(ui.Modal):
    """Modal para coletar código de cupom (opcional)"""
    
    def __init__(self, user, guild, product):
        super().__init__(
            title="Cupom de Desconto (Opcional)", 
            timeout=600,
            custom_id=f"modal_coupon_{user.id}_{product['id']}"
        )
        self.user = user
        self.guild = guild
        self.product = product
        
        self.add_item(ui.InputText(
            label="Código do Cupom",
            placeholder="Digite o código do cupom ou deixe em branco",
            required=False,
            max_length=50
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa o cupom e cria o ticket"""
        print(f"🔧 MODAL SUBMIT: CouponInputModal iniciado por {interaction.user.name}")
        
        try:
            # Verificar se interaction ainda é válida
            if interaction.response.is_done():
                print("❌ Interaction já foi respondida!")
                return
                
            coupon_code = self.children[0].value.strip() if self.children[0].value else None
            
            # Importar TicketManager e criar instância com bot
            from utils.ticket_manager import TicketManager
            ticket_manager = TicketManager(interaction.client)
            
            success, message = await ticket_manager.create_ticket(
                self.user,
                self.guild,
                self.product,
                coupon_code=coupon_code
            )
            
            if success:
                await interaction.response.send_message(f"✅ {message}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao processar cupom: {e}")
            import traceback
            traceback.print_exc()
            
            # Mensagem de erro mais informativa
            error_message = str(e) if str(e) else "Erro desconhecido ao criar ticket"
            
            # Tentar enviar mensagem de erro
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        f"❌ **Algo deu errado, tente novamente.**\n\n"
                        f"Detalhes técnicos: {error_message[:100]}",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        f"❌ **Algo deu errado, tente novamente.**\n\n"
                        f"Detalhes técnicos: {error_message[:100]}",
                        ephemeral=True
                    )
            except Exception as e2:
                print(f"❌ Falha ao enviar mensagem de erro: {e2}")
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        """Handler de erros do modal"""
        print(f"❌ ERRO NO MODAL CouponInputModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Erro ao processar cupom: {str(error)[:100]}", 
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Erro ao processar cupom: {str(error)[:100]}", 
                    ephemeral=True
                )
        except Exception as e:
            print(f"❌ Falha ao enviar mensagem de erro do on_error: {e}")

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
        super().__init__(
            title="Criar Novo Cupom", 
            timeout=600,
            custom_id="modal_create_coupon"
        )
        
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
        print(f"🔧 MODAL SUBMIT: CreateCouponModal iniciado por {interaction.user.name}")
        
        try:
            # Verificar se interaction ainda é válida
            if interaction.response.is_done():
                print("❌ Interaction já foi respondida!")
                return
                
            from models.coupon_model import CouponModel
            from datetime import datetime
            
            code = self.children[0].value.upper().strip()
            discount = float(self.children[1].value.strip())
            max_uses = int(self.children[2].value.strip()) if self.children[2].value.strip() and self.children[2].value.strip() != "0" else None
            one_per_user = self.children[3].value.strip().lower() == "sim"
            expires_str = self.children[4].value.strip()
            
            # Validar desconto
            if discount < 1 or discount > 100:
                await interaction.response.send_message("❌ Desconto deve estar entre 1% e 100%!", ephemeral=True)
                return
            
            # Processar data de expiração
            expires_at = None
            if expires_str:
                try:
                    expires_at = datetime.strptime(expires_str, "%d/%m/%Y").isoformat()
                except:
                    await interaction.response.send_message("❌ Data inválida! Use formato DD/MM/YYYY", ephemeral=True)
                    return
            
            # Criar cupom
            coupon_data = {
                'code': code,
                'discount_percent': discount,
                'max_uses': max_uses,
                'one_per_user': one_per_user,
                'expires_at': expires_at,
                'created_by': interaction.user.id,
                'active': True
            }
            
            coupon_model = CouponModel()
            success, message = await coupon_model.create_coupon(coupon_data)
            
            if success:
                embed = discord.Embed(
                    title="✅ Cupom Criado!",
                    description=f"Cupom **{code}** criado com sucesso!",
                    color=0x00ff00
                )
                embed.add_field(name="Desconto", value=f"{discount}%", inline=True)
                embed.add_field(name="Limite", value=str(max_uses) if max_uses else "Ilimitado", inline=True)
                embed.add_field(name="Um por usuário", value="Sim" if one_per_user else "Não", inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Valores inválidos! Verifique desconto e limite.", ephemeral=True)
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao criar cupom: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar enviar mensagem de erro
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Erro ao criar cupom.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erro ao criar cupom.", ephemeral=True)
            except Exception as e2:
                print(f"❌ Falha ao enviar mensagem de erro: {e2}")
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL CreateCouponModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

class SetupSupportModal(ui.Modal):
    """Modal para configurar o sistema de tickets de suporte com select menu"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            title="Configurar Tickets de Suporte", 
            timeout=600,
            custom_id="modal_setup_support"
        )
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
        print(f"🔧 MODAL SUBMIT: SetupSupportModal iniciado por {interaction.user.name}")
        
        try:
            # Verificar se interaction ainda é válida
            if interaction.response.is_done():
                print("❌ Interaction já foi respondida!")
                return
                
            print(f"Modal de suporte submetido por {interaction.user.name}")
            titulo = self.children[0].value.strip()
            descricao = self.children[1].value.strip()
            opcoes_text = self.children[2].value.strip()
            botao_config = self.children[3].value.strip()
            cor_hex = self.children[4].value.strip()
            
            # Processar configuração do botão (Nome | Emoji)
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
            linhas = opcoes_text.split('\n')
            
            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                
                # Formato: EMOJI|Nome|Descrição
                partes = linha.split('|')
                if len(partes) >= 3:
                    emoji = partes[0].strip()
                    nome = partes[1].strip()
                    desc = partes[2].strip()
                    opcoes_config.append({
                        'emoji': emoji,
                        'nome': nome,
                        'descricao': desc
                    })
                elif len(partes) == 2:
                    # Formato sem descrição: EMOJI|Nome
                    emoji = partes[0].strip()
                    nome = partes[1].strip()
                    opcoes_config.append({
                        'emoji': emoji,
                        'nome': nome,
                        'descricao': f"Abrir ticket de {nome.lower()}"
                    })
            
            if not opcoes_config:
                await interaction.response.send_message("❌ Nenhuma opção válida configurada! Use o formato: EMOJI|Nome|Descrição", ephemeral=True)
                return
            
            if len(opcoes_config) > 25:
                await interaction.response.send_message("❌ Máximo de 25 opções permitidas no select menu!", ephemeral=True)
                return
            
            # Converter cor hex para int
            try:
                cor_hex = cor_hex.strip().lower()
                
                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]
                
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                
                cor_int = int(cor_hex, 16)
                print(f"Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0x5865F2  # Azul Discord padrão
            
            # Criar embed
            embed = discord.Embed(
                title=titulo,
                description=descricao if descricao else None,
                color=cor_int
            )
            
            # Adicionar cada opção como field
            for opt in opcoes_config:
                embed.add_field(
                    name=f"{opt['emoji']} {opt['nome']}",
                    value=opt['descricao'],
                    inline=False
                )
            
            # Criar view com botão que abre select menu
            view = MultiSupportTicketView(opcoes_config, label_botao, emoji_botao)
            
            await interaction.response.send_message(embed=embed, view=view)
            print(f"Modal de suporte processado com sucesso - {len(opcoes_config)} opções criadas")
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao configurar sistema de suporte: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar enviar mensagem de erro
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Erro ao configurar sistema de suporte.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Erro ao configurar sistema de suporte.", ephemeral=True)
            except Exception as e2:
                print(f"❌ Falha ao enviar mensagem de erro: {e2}")
    
    async def on_error(self, error: Exception, interaction: discord.Interaction):
        print(f"❌ ERRO NO MODAL SetupSupportModal: {error}")
        import traceback
        traceback.print_exc()
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erro: {str(error)[:100]}", ephemeral=True)
        except:
            pass

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
