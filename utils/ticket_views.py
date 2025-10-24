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
        super().__init__(title="Criar Mensagem Embed", timeout=300)
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
        try:
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
            await interaction.response.send_message(embed=embed)
            print("Mensagem embed criada com sucesso")
            
        except Exception as e:
            print(f"Erro ao criar mensagem embed: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao criar mensagem embed.", ephemeral=True)

class SetupTicketModal(ui.Modal):
    """Modal para configurar o sistema de tickets"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Configurar Sistema de Tickets", timeout=300)
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
        try:
            print(f"Modal submetido por {interaction.user.name}")
            headline = self.children[0].value
            descricao = self.children[1].value
            product_ids_input = self.children[2].value.strip()
            nome_botao = self.children[3].value
            cor_hex = self.children[4].value.strip()
            
            print(f"Valores: {headline}, {descricao}, {nome_botao}, produtos: {product_ids_input}, {cor_hex}")
            
            # Processar IDs dos produtos
            allowed_product_ids = None
            if product_ids_input:
                try:
                    # Converter string "1,2,3" para lista de inteiros
                    allowed_product_ids = [int(pid.strip()) for pid in product_ids_input.split(',') if pid.strip()]
                    print(f"✅ Produtos filtrados: {allowed_product_ids}")
                except ValueError:
                    await interaction.response.send_message(
                        "❌ IDs de produtos inválidos! Use números separados por vírgula (ex: 1,2,3)",
                        ephemeral=True
                    )
                    return
            
            # Salvar configuração no banco de dados
            from models.guild_config_model import GuildConfigModel
            guild_config = GuildConfigModel()
            
            success = await guild_config.set_ticket_product_filter(
                guild_id=interaction.guild_id,
                product_ids=allowed_product_ids
            )
            
            if success:
                if allowed_product_ids:
                    print(f"✅ Filtro de produtos salvo: {allowed_product_ids}")
                else:
                    print(f"✅ Filtro removido - todos produtos disponíveis")
            
            # Converter cor hex para int
            try:
                # Limpar a string de cor
                cor_hex = cor_hex.strip().lower()
                
                if cor_hex.startswith('#'):
                    cor_hex = cor_hex[1:]  # Remove #
                elif cor_hex.startswith('0x'):
                    cor_hex = cor_hex[2:]  # Remove 0x
                
                # Garantir que tem 6 caracteres
                if len(cor_hex) == 3:
                    cor_hex = cor_hex[0] + cor_hex[0] + cor_hex[1] + cor_hex[1] + cor_hex[2] + cor_hex[2]
                
                cor_int = int(cor_hex, 16)
                print(f"Cor convertida: {cor_int} (0x{cor_hex})")
            except (ValueError, IndexError) as e:
                print(f"Cor inválida '{cor_hex}', usando padrão. Erro: {e}")
                cor_int = 0x0099ff  # Azul padrão
            
            # Criar embed com as configurações
            embed = discord.Embed(
                title=headline,
                description=descricao,
                color=cor_int
            )
            
            embed.add_field(
                name="🚀 Como Funciona?",
                value="1. Clique no botão abaixo para criar um ticket\n2. Escolha o produto no modal\n3. Um canal privado será criado para você\n4. O bot irá guiá-lo para o pagamento e entrega",
                inline=False
            )
            
            # Adicionar info sobre filtro de produtos
            if allowed_product_ids:
                embed.add_field(
                    name="🔍 Produtos Filtrados",
                    value=f"Apenas os produtos com IDs: **{', '.join(map(str, allowed_product_ids))}** aparecerão neste ticket.",
                    inline=False
                )
            
            embed.set_footer(text="Atendimento 24/7 • Pagamento via Pix")
            
            # Criar view com botão personalizado
            view = TicketView(nome_botao)
            
            await interaction.response.send_message(embed=embed, view=view)
            print("Modal processado com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar sistema de tickets: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao configurar sistema de tickets.", ephemeral=True)

class CouponInputModal(ui.Modal):
    """Modal para coletar código de cupom (opcional)"""
    
    def __init__(self, user, guild, product):
        super().__init__(title="Cupom de Desconto (Opcional)", timeout=180)
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
        try:
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
            await interaction.response.send_message(
                f"❌ **Algo deu errado, tente novamente.**\n\n"
                f"Detalhes técnicos: {error_message[:100]}",
                ephemeral=True
            )

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
        super().__init__(timeout=300)
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
        super().__init__(title="Criar Novo Cupom", timeout=300)
        
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
        try:
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
            print(f"Erro ao criar cupom: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao criar cupom.", ephemeral=True)

class SetupSupportModal(ui.Modal):
    """Modal para configurar o sistema de tickets de suporte com select menu"""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Configurar Tickets de Suporte", timeout=300)
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
        try:
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
            print(f"Erro ao configurar sistema de suporte: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message("❌ Erro ao configurar sistema de suporte.", ephemeral=True)

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
