import discord
from models.transaction_model import TransactionModel
from models.product_model import ProductModel
from models.inventory_model import InventoryModel
from utils.vip_manager import VipManager
from typing import Optional
from datetime import datetime

class DeliveryManager:
    """Gerencia a entrega automática de produtos digitais"""
    
    def __init__(self, bot):
        self.bot = bot
        self.transaction_model = TransactionModel()
        self.product_model = ProductModel()
        self.inventory_model = InventoryModel()
        self.vip_manager = VipManager(bot)
    
    async def process_payment_confirmation(self, transaction_id: int, payment_id: str = None) -> bool:
        """
        Processa confirmação de pagamento e entrega o produto
        
        Args:
            transaction_id: ID da transação
            payment_id: ID do pagamento na PushinPay (opcional)
        
        Returns:
            True se entrega foi bem sucedida, False caso contrário
        """
        try:
            print(f"📦 Processando entrega para transação #{transaction_id}")
            
            # 1. Buscar transação
            transaction = await self.transaction_model.get_transaction(transaction_id)
            if not transaction:
                print(f"❌ Transação #{transaction_id} não encontrada")
                return False
            
            # 2. Verificar se já foi entregue
            if transaction.get('status') == 'completed':
                print(f"⚠️ Transação #{transaction_id} já foi entregue anteriormente")
                return False
            
            # 3. Buscar produto
            product = await self.product_model.get_product_by_id(transaction['product_id'])
            if not product:
                print(f"❌ Produto #{transaction['product_id']} não encontrado")
                return False
            
            # 3.5. Verificar se é produto VIP
            if product.get('category') == 'VIP' or product.get('vip_config'):
                return await self._process_vip_delivery(transaction, product, payment_id)
            
            # 4. Buscar item do estoque (se já foi reservado)
            inventory_item = await self.inventory_model.get_inventory_by_transaction(transaction_id)
            
            # 5. Se não foi reservado ainda, tentar reservar agora
            if not inventory_item:
                inventory_item = await self.inventory_model.get_available_stock(transaction['product_id'])
                
                if not inventory_item:
                    # Sem estoque disponível
                    await self._handle_out_of_stock(transaction, product)
                    return False
                
                # Reservar o item
                reserved = await self.inventory_model.reserve_stock(
                    inventory_item['id'],
                    transaction['user_id'],
                    transaction_id
                )
                
                if not reserved:
                    print(f"❌ Falha ao reservar estoque para transação #{transaction_id}")
                    return False
            
            # 6. Marcar estoque como vendido
            sold = await self.inventory_model.mark_as_sold(inventory_item['id'])
            if not sold:
                print(f"⚠️ Falha ao marcar estoque como vendido (transação #{transaction_id})")
            
            # 7. Enviar produto para o usuário
            delivery_success = await self._deliver_product(transaction, product, inventory_item)
            
            if not delivery_success:
                print(f"❌ Falha ao entregar produto para transação #{transaction_id}")
                return False
            
            # 8. Atualizar transação como completada
            update_data = {
                'status': 'completed',
                'delivered_at': datetime.now().isoformat(),
                'inventory_id': inventory_item['id']
            }
            
            if payment_id:
                update_data['payment_id'] = payment_id
            
            await self.transaction_model.update_transaction(transaction_id, update_data)
            
            # 9. Notificar admin
            await self._notify_admin_delivery_success(transaction, product)
            
            # 10. Fechar ticket após 5 minutos
            await self._schedule_ticket_close(transaction)
            
            print(f"✅ Produto entregue com sucesso para transação #{transaction_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao processar entrega: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _deliver_product(self, transaction: dict, product: dict, inventory_item: dict) -> bool:
        """Envia o produto para o canal do ticket"""
        try:
            # Buscar canal da entrega
            channel_id = transaction.get('delivery_channel_id')
            if not channel_id:
                print(f"⚠️ Canal de entrega não encontrado para transação #{transaction['id']}")
                return False
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"❌ Canal {channel_id} não encontrado")
                return False
            
            # Buscar usuário
            user = self.bot.get_user(transaction['user_id'])
            if not user:
                try:
                    user = await self.bot.fetch_user(transaction['user_id'])
                except:
                    print(f"❌ Usuário {transaction['user_id']} não encontrado")
                    return False
            
            # Criar embed de entrega
            embed = discord.Embed(
                title="✅ Produto Entregue!",
                description=f"Seu pagamento foi confirmado e o produto foi entregue.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📦 Produto",
                value=f"**{product['name']}**",
                inline=False
            )
            
            # Mostrar valores com desconto se houver cupom
            if transaction.get('discount_amount') and transaction['discount_amount'] > 0:
                valor_original = transaction.get('amount', 0)
                desconto = transaction.get('discount_amount', 0)
                valor_final = transaction.get('final_amount', valor_original)
                
                valor_text = f"~~R$ {valor_original:.2f}~~ → **R$ {valor_final:.2f}**\n🎟️ Desconto: R$ {desconto:.2f}"
                embed.add_field(
                    name="💰 Valor Pago",
                    value=valor_text,
                    inline=True
                )
            else:
                valor_pago = transaction.get('final_amount', transaction.get('amount', 0))
                embed.add_field(
                    name="💰 Valor Pago",
                    value=f"R$ {valor_pago:.2f}",
                    inline=True
                )
            
            embed.add_field(
                name="📅 Data da Compra",
                value=f"<t:{int(datetime.now().timestamp())}:F>",
                inline=True
            )
            
            embed.add_field(
                name="🔑 Seu Produto",
                value=f"```\n{inventory_item['content']}\n```",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Importante",
                value="• Guarde essas informações em local seguro\n• Não compartilhe com terceiros\n• Este canal será fechado em 5 minutos",
                inline=False
            )
            
            embed.set_footer(text="Obrigado pela sua compra! 💙")
            
            # Enviar no canal do ticket
            await channel.send(f"{user.mention}", embed=embed)
            
            # Enviar também por DM (versão completa)
            try:
                dm_embed = discord.Embed(
                    title="🎉 Compra Confirmada!",
                    description=f"Olá {user.mention}! Seu pagamento foi confirmado com sucesso.",
                    color=0x00ff00,
                    timestamp=datetime.now()
                )
                
                dm_embed.add_field(
                    name="📦 Produto Adquirido",
                    value=f"**{product['name']}**\n{product.get('description', 'Produto digital')}",
                    inline=False
                )
                
                # Mostrar valores com desconto se houver cupom
                if transaction.get('discount_amount') and transaction['discount_amount'] > 0:
                    valor_original = transaction.get('amount', 0)
                    desconto = transaction.get('discount_amount', 0)
                    valor_final = transaction.get('final_amount', valor_original)
                    
                    valor_text = f"~~R$ {valor_original:.2f}~~ → **R$ {valor_final:.2f}**"
                    dm_embed.add_field(
                        name="💰 Valor Pago",
                        value=valor_text,
                        inline=True
                    )
                    dm_embed.add_field(
                        name="🎟️ Desconto Aplicado",
                        value=f"R$ {desconto:.2f}",
                        inline=True
                    )
                else:
                    valor_pago = transaction.get('final_amount', transaction.get('amount', 0))
                    dm_embed.add_field(
                        name="💰 Valor Pago",
                        value=f"R$ {valor_pago:.2f}",
                        inline=True
                    )
                
                dm_embed.add_field(
                    name="📅 Data da Compra",
                    value=f"<t:{int(datetime.now().timestamp())}:F>",
                    inline=True
                )
                
                dm_embed.add_field(
                    name="🔑 Seu Produto",
                    value=f"```\n{inventory_item['content']}\n```",
                    inline=False
                )
                
                dm_embed.add_field(
                    name="⚠️ Importante",
                    value="• Guarde essas informações em local seguro\n• Não compartilhe com terceiros\n• Este é seu comprovante de compra",
                    inline=False
                )
                
                dm_embed.set_footer(
                    text=f"Compra #{transaction['id']} • Obrigado pela preferência! 💙",
                    icon_url=user.display_avatar.url if user.display_avatar else None
                )
                
                await user.send(embed=dm_embed)
                print(f"✉️ Produto completo enviado por DM para {user.name}")
                
                # Adicionar mensagem no canal informando sobre a DM
                await channel.send(
                    f"📬 {user.mention} Uma cópia completa também foi enviada na sua DM!",
                    delete_after=30
                )
                
            except discord.Forbidden:
                print(f"⚠️ {user.name} está com DMs desabilitadas")
                await channel.send(
                    f"⚠️ {user.mention} Não consegui enviar uma cópia na sua DM. Verifique se suas mensagens diretas estão habilitadas!",
                    delete_after=60
                )
            except Exception as e:
                print(f"⚠️ Erro ao enviar DM para {user.name}: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao entregar produto: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _handle_out_of_stock(self, transaction: dict, product: dict):
        """Trata caso de estoque esgotado"""
        try:
            print(f"⚠️ ESTOQUE ESGOTADO: {product['name']} (ID: {product['id']})")
            
            # Atualizar transação
            await self.transaction_model.update_transaction(
                transaction['id'],
                {'status': 'out_of_stock'}
            )
            
            # Notificar admin
            await self._notify_admin_out_of_stock(transaction, product)
            
            # Notificar cliente
            channel = self.bot.get_channel(transaction.get('delivery_channel_id'))
            if channel:
                embed = discord.Embed(
                    title="⚠️ Estoque Temporariamente Esgotado",
                    description=f"O produto **{product['name']}** está temporariamente sem estoque.",
                    color=0xffa500
                )
                embed.add_field(
                    name="💰 Seu Pagamento",
                    value="Seu pagamento foi confirmado e será processado assim que repormos o estoque.",
                    inline=False
                )
                embed.add_field(
                    name="⏱️ Prazo",
                    value="Você receberá o produto em até 24 horas.\nSe preferir, pode solicitar reembolso.",
                    inline=False
                )
                await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao tratar estoque esgotado: {e}")
    
    async def _notify_admin_delivery_success(self, transaction: dict, product: dict):
        """Notifica admin sobre entrega bem sucedida"""
        try:
            # Buscar canal de logs (você pode adicionar isso no config)
            # Por enquanto, apenas log no console
            print(f"📊 ENTREGA CONFIRMADA: {product['name']} para usuário {transaction['user_id']}")
        except Exception as e:
            print(f"Erro ao notificar admin: {e}")
    
    async def _notify_admin_out_of_stock(self, transaction: dict, product: dict):
        """Notifica admin sobre estoque esgotado"""
        try:
            print(f"🚨 ALERTA: Estoque esgotado de {product['name']} - Transação #{transaction['id']} aguardando")
        except Exception as e:
            print(f"Erro ao notificar admin: {e}")
    
    async def _process_vip_delivery(self, transaction: dict, product: dict, payment_id: str = None) -> bool:
        """
        Processa a entrega de um produto VIP
        
        Args:
            transaction: Dados da transação
            product: Dados do produto VIP
            payment_id: ID do pagamento na PushinPay
        
        Returns:
            True se entrega foi bem sucedida
        """
        try:
            print(f"👑 Processando entrega VIP para transação #{transaction['id']}")
            
            # Buscar canal da entrega
            channel_id = transaction.get('delivery_channel_id')
            if not channel_id:
                print(f"⚠️ Canal de entrega não encontrado para transação #{transaction['id']}")
                return False
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                print(f"❌ Canal {channel_id} não encontrado")
                return False
            
            # Buscar membro
            guild = channel.guild
            member = guild.get_member(transaction['user_id'])
            
            if not member:
                try:
                    member = await guild.fetch_member(transaction['user_id'])
                except:
                    print(f"❌ Membro {transaction['user_id']} não encontrado no servidor")
                    return False
            
            # Processar compra VIP
            subscription = await self.vip_manager.process_vip_purchase(
                member=member,
                product=product,
                transaction_id=transaction['id']
            )
            
            if not subscription:
                print(f"❌ Falha ao processar compra VIP")
                
                # Notificar no canal
                embed = discord.Embed(
                    title="❌ Erro ao Ativar VIP",
                    description="Houve um erro ao ativar sua assinatura VIP. A equipe foi notificada e resolverá em breve.",
                    color=discord.Color.red()
                )
                await channel.send(f"{member.mention}", embed=embed)
                
                return False
            
            # Atualizar transação como completada
            update_data = {
                'status': 'completed',
                'delivered_at': datetime.now().isoformat()
            }
            
            if payment_id:
                update_data['payment_id'] = payment_id
            
            await self.transaction_model.update_transaction(transaction['id'], update_data)
            
            # Enviar confirmação no canal do ticket
            embed = discord.Embed(
                title="✅ VIP Ativado com Sucesso!",
                description=f"{member.mention} Sua assinatura VIP foi ativada!",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👑 Role VIP",
                value=f"**{subscription['role_name']}**",
                inline=True
            )
            
            # Informações de duração
            if subscription['duration_days'] is None:
                duration_text = "🌟 **VITALÍCIO**"
            else:
                expires_at = datetime.fromisoformat(subscription['expires_at'].replace('Z', '+00:00'))
                duration_text = f"⏰ **{subscription['duration_days']} dias**\nExpira: <t:{int(expires_at.timestamp())}:R>"
            
            embed.add_field(
                name="📅 Duração",
                value=duration_text,
                inline=True
            )
            
            # Mostrar valores com desconto se houver cupom
            if transaction.get('discount_amount') and transaction['discount_amount'] > 0:
                valor_original = transaction.get('amount', 0)
                desconto = transaction.get('discount_amount', 0)
                valor_final = transaction.get('final_amount', valor_original)
                
                valor_text = f"~~R$ {valor_original:.2f}~~ → **R$ {valor_final:.2f}**\n🎟️ Desconto: R$ {desconto:.2f}"
                embed.add_field(
                    name="💰 Valor Pago",
                    value=valor_text,
                    inline=False
                )
            else:
                valor_pago = transaction.get('final_amount', transaction.get('amount', 0))
                embed.add_field(
                    name="💰 Valor Pago",
                    value=f"R$ {valor_pago:.2f}",
                    inline=False
                )
            
            embed.add_field(
                name="✨ Benefícios VIP",
                value="• Acesso a canais exclusivos\n• Prioridade no suporte\n• Descontos especiais\n• Conteúdo exclusivo",
                inline=False
            )
            
            embed.add_field(
                name="📬 Mensagem Privada",
                value="Enviamos todos os detalhes da sua assinatura na sua DM!",
                inline=False
            )
            
            embed.set_footer(text="Aproveite seus benefícios VIP! 👑")
            
            await channel.send(embed=embed)
            
            # Notificar admin sobre venda VIP
            await self._notify_admin_vip_sale(transaction, product, subscription)
            
            # Fechar ticket após 2 minutos
            await self._schedule_ticket_close(transaction)
            
            print(f"✅ VIP entregue com sucesso para transação #{transaction['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao processar entrega VIP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _notify_admin_vip_sale(self, transaction: dict, product: dict, subscription: dict):
        """Notifica admin sobre venda VIP"""
        try:
            print(f"👑 VENDA VIP: {product['name']} para usuário {transaction['user_id']} - {subscription['role_name']}")
        except Exception as e:
            print(f"Erro ao notificar admin sobre venda VIP: {e}")
    
    async def _schedule_ticket_close(self, transaction: dict):
        """Agenda fechamento do ticket após 5 minutos"""
        try:
            import asyncio
            
            # Aguardar 5 minutos
            await asyncio.sleep(300)
            
            # Buscar canal e fechar
            channel_id = transaction.get('delivery_channel_id')
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title="🔒 Ticket Fechado",
                        description="Este ticket foi fechado automaticamente após a entrega do produto.",
                        color=0x808080
                    )
                    await channel.send(embed=embed)
                    
                    # Aguardar 10 segundos e deletar canal
                    await asyncio.sleep(10)
                    await channel.delete(reason="Entrega concluída - Ticket fechado automaticamente")
                    print(f"🔒 Ticket fechado: {channel.name}")
        except Exception as e:
            print(f"Erro ao fechar ticket: {e}")

