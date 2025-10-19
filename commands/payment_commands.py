import discord
from discord.ext import commands
from models.transaction_model import TransactionModel
from utils.payment_utils import PaymentUtils

class PaymentCommands(commands.Cog):
    """Comandos relacionados ao pagamento"""
    
    def __init__(self, bot):
        self.bot = bot
        self.transaction_model = TransactionModel()
        self.payment_utils = PaymentUtils()
    
    @commands.command(name='payment_history')
    async def payment_history(self, ctx):
        """Exibe o histórico de pagamentos do usuário"""
        try:
            user_id = ctx.author.id
            transactions = await self.transaction_model.get_user_transactions(user_id)
            
            if not transactions:
                await ctx.send("❌ Nenhuma transação encontrada para você.")
                return
            
            embed = discord.Embed(
                title="📊 Histórico de Pagamentos",
                description=f"Transações de {ctx.author.name}:",
                color=0x0099ff
            )
            
            for transaction in transactions[:10]:  # Limitar a 10 transações
                status_emoji = {
                    'pending': '⏳',
                    'approved': '✅',
                    'failed': '❌',
                    'cancelled': '🚫'
                }.get(transaction['status'], '❓')
                
                embed.add_field(
                    name=f"{status_emoji} Transação #{transaction['id']}",
                    value=f"**Valor:** R$ {transaction['amount']:.2f}\n**Status:** {transaction['status'].upper()}\n**Data:** {transaction['created_at'].strftime('%d/%m/%Y %H:%M')}",
                    inline=True
                )
            
            if len(transactions) > 10:
                embed.set_footer(text=f"Mostrando 10 de {len(transactions)} transações")
            else:
                embed.set_footer(text=f"Total: {len(transactions)} transações")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            await ctx.send("❌ Erro ao carregar histórico de pagamentos.")
    
    @commands.command(name='payment_details')
    async def payment_details(self, ctx, transaction_id: int):
        """Exibe detalhes de uma transação específica"""
        try:
            transaction = await self.transaction_model.get_transaction(transaction_id)
            
            if not transaction:
                await ctx.send("❌ Transação não encontrada.")
                return
            
            # Verificar se a transação pertence ao usuário
            if transaction['user_id'] != ctx.author.id:
                await ctx.send("❌ Você não tem permissão para ver esta transação.")
                return
            
            embed = discord.Embed(
                title=f"📋 Detalhes da Transação #{transaction_id}",
                color=0x0099ff
            )
            
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'failed': '❌',
                'cancelled': '🚫'
            }.get(transaction['status'], '❓')
            
            embed.add_field(
                name="📈 Status",
                value=f"{status_emoji} {transaction['status'].upper()}",
                inline=True
            )
            embed.add_field(
                name="💰 Valor",
                value=f"R$ {transaction['amount']:.2f}",
                inline=True
            )
            embed.add_field(
                name="📧 Email",
                value=transaction.get('email', 'N/A'),
                inline=True
            )
            
            if transaction.get('pix_code'):
                embed.add_field(
                    name="🔢 Código Pix",
                    value=f"```{transaction['pix_code']}```",
                    inline=False
                )
            
            if transaction.get('payment_id'):
                embed.add_field(
                    name="🆔 ID do Pagamento",
                    value=transaction['payment_id'],
                    inline=True
                )
            
            embed.add_field(
                name="📅 Data de Criação",
                value=transaction['created_at'].strftime("%d/%m/%Y %H:%M:%S"),
                inline=True
            )
            
            if transaction.get('updated_at'):
                embed.add_field(
                    name="📅 Última Atualização",
                    value=transaction['updated_at'].strftime("%d/%m/%Y %H:%M:%S"),
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ ID da transação deve ser um número.")
        except Exception as e:
            print(f"Erro ao buscar detalhes da transação: {e}")
            await ctx.send("❌ Erro ao carregar detalhes da transação.")
    
    @commands.command(name='cancel_payment')
    async def cancel_payment(self, ctx, transaction_id: int):
        """Cancela uma transação pendente"""
        try:
            transaction = await self.transaction_model.get_transaction(transaction_id)
            
            if not transaction:
                await ctx.send("❌ Transação não encontrada.")
                return
            
            # Verificar se a transação pertence ao usuário
            if transaction['user_id'] != ctx.author.id:
                await ctx.send("❌ Você não tem permissão para cancelar esta transação.")
                return
            
            # Verificar se a transação pode ser cancelada
            if transaction['status'] != 'pending':
                await ctx.send("❌ Apenas transações pendentes podem ser canceladas.")
                return
            
            # Atualizar status para cancelado
            await self.transaction_model.update_transaction(transaction_id, {'status': 'cancelled'})
            
            embed = discord.Embed(
                title="🚫 Transação Cancelada",
                description=f"Transação #{transaction_id} foi cancelada com sucesso.",
                color=0xff0000
            )
            embed.add_field(
                name="💰 Valor Devolvido",
                value=f"R$ {transaction['amount']:.2f}",
                inline=True
            )
            embed.add_field(
                name="📅 Data do Cancelamento",
                value=ctx.message.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ ID da transação deve ser um número.")
        except Exception as e:
            print(f"Erro ao cancelar transação: {e}")
            await ctx.send("❌ Erro ao cancelar transação.")

async def setup(bot):
    await bot.add_cog(PaymentCommands(bot))
