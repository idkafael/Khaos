"""
Modelo de Carteira Virtual
Gerencia saldo dos servidores, transações e histórico financeiro
"""

from supabase import create_client
from config.config import Config
from decimal import Decimal
from typing import Optional, Dict, List
from datetime import datetime

class WalletModel:
    """Modelo para gerenciar carteira virtual dos servidores"""
    
    def __init__(self):
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.SALE_FEE = Decimal('0.80')  # Taxa fixa por venda: R$ 0,80
        self.WITHDRAWAL_FEE_PERCENT = Decimal('3.00')  # Taxa de saque: 3%
        self.MIN_WITHDRAWAL = Decimal('10.00')  # Saque mínimo: R$ 10,00
    
    async def get_wallet(self, guild_id: int) -> Optional[Dict]:
        """
        Busca carteira de um servidor
        
        Args:
            guild_id: ID do servidor Discord
            
        Returns:
            Dict com dados da carteira ou None se não existir
        """
        try:
            response = self.supabase.table('guild_wallets').select('*').eq('guild_id', guild_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar carteira: {e}")
            return None
    
    async def get_or_create_wallet(self, guild_id: int) -> Dict:
        """
        Busca ou cria carteira do servidor
        
        Args:
            guild_id: ID do servidor Discord
            
        Returns:
            Dict com dados da carteira
        """
        wallet = await self.get_wallet(guild_id)
        
        if not wallet:
            # Criar carteira nova
            try:
                response = self.supabase.table('guild_wallets').insert({
                    'guild_id': guild_id,
                    'balance_available': 0.00,
                    'balance_pending': 0.00,
                    'total_earned': 0.00,
                    'total_withdrawn': 0.00,
                    'platform_fees_paid': 0.00
                }).execute()
                
                wallet = response.data[0] if response.data else None
                print(f"✅ Carteira criada para servidor {guild_id}")
                
            except Exception as e:
                print(f"❌ Erro ao criar carteira: {e}")
                return None
        
        return wallet
    
    async def credit_wallet(self, guild_id: int, amount: Decimal, transaction_id: int, 
                           description: str = None) -> bool:
        """
        Credita valor na carteira após venda (desconta taxa de R$ 0,80)
        
        Args:
            guild_id: ID do servidor
            amount: Valor bruto da venda
            transaction_id: ID da transação
            description: Descrição opcional
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Usar função SQL que já calcula tudo
            self.supabase.rpc('credit_wallet_from_sale', {
                'p_guild_id': guild_id,
                'p_transaction_id': transaction_id,
                'p_gross_amount': float(amount),
                'p_platform_fee': float(self.SALE_FEE)
            }).execute()
            
            net_amount = amount - self.SALE_FEE
            print(f"💰 Carteira creditada: R$ {net_amount:.2f} (bruto: R$ {amount:.2f}, taxa: R$ {self.SALE_FEE:.2f})")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao creditar carteira: {e}")
            return False
    
    async def debit_wallet(self, guild_id: int, amount: Decimal, withdrawal_id: int) -> bool:
        """
        Debita valor da carteira para saque
        
        Args:
            guild_id: ID do servidor
            amount: Valor a ser sacado
            withdrawal_id: ID da solicitação de saque
            
        Returns:
            True se sucesso, False se saldo insuficiente ou erro
        """
        try:
            # Usar função SQL que valida saldo e debita
            response = self.supabase.rpc('debit_wallet_from_withdrawal', {
                'p_guild_id': guild_id,
                'p_withdrawal_id': withdrawal_id,
                'p_amount': float(amount),
                'p_fee_percent': float(self.WITHDRAWAL_FEE_PERCENT)
            }).execute()
            
            success = response.data if response.data else False
            
            if success:
                fee = amount * (self.WITHDRAWAL_FEE_PERCENT / 100)
                print(f"💸 Carteira debitada: R$ {amount:.2f} (taxa: R$ {fee:.2f})")
            else:
                print(f"❌ Saldo insuficiente para saque de R$ {amount:.2f}")
            
            return success
            
        except Exception as e:
            print(f"❌ Erro ao debitar carteira: {e}")
            return False
    
    async def get_balance(self, guild_id: int) -> Decimal:
        """
        Retorna saldo disponível do servidor
        
        Args:
            guild_id: ID do servidor
            
        Returns:
            Saldo disponível (Decimal)
        """
        wallet = await self.get_wallet(guild_id)
        
        if wallet:
            return Decimal(str(wallet.get('balance_available', 0)))
        return Decimal('0.00')
    
    async def can_withdraw(self, guild_id: int, amount: Decimal) -> tuple[bool, str]:
        """
        Verifica se servidor pode sacar o valor solicitado
        
        Args:
            guild_id: ID do servidor
            amount: Valor a sacar
            
        Returns:
            Tuple (pode_sacar: bool, mensagem: str)
        """
        # Validar valor mínimo
        if amount < self.MIN_WITHDRAWAL:
            return False, f"❌ Valor mínimo para saque é R$ {self.MIN_WITHDRAWAL:.2f}"
        
        # Verificar saldo
        balance = await self.get_balance(guild_id)
        
        if balance < amount:
            return False, f"❌ Saldo insuficiente. Disponível: R$ {balance:.2f}"
        
        return True, "✅ Saque autorizado"
    
    async def calculate_withdrawal_fees(self, amount: Decimal) -> Dict:
        """
        Calcula taxas de saque
        
        Args:
            amount: Valor a sacar
            
        Returns:
            Dict com: amount_requested, fee_amount, net_amount
        """
        fee_amount = (amount * (self.WITHDRAWAL_FEE_PERCENT / 100)).quantize(Decimal('0.01'))
        net_amount = amount - fee_amount
        
        return {
            'amount_requested': amount,
            'fee_amount': fee_amount,
            'fee_percent': self.WITHDRAWAL_FEE_PERCENT,
            'net_amount': net_amount
        }
    
    async def get_wallet_history(self, guild_id: int, limit: int = 50) -> List[Dict]:
        """
        Busca histórico de transações da carteira
        
        Args:
            guild_id: ID do servidor
            limit: Número de transações a retornar
            
        Returns:
            Lista de transações
        """
        try:
            response = self.supabase.table('wallet_transactions')\
                .select('*')\
                .eq('guild_id', guild_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    async def get_wallet_stats(self, guild_id: int) -> Dict:
        """
        Retorna estatísticas da carteira
        
        Args:
            guild_id: ID do servidor
            
        Returns:
            Dict com estatísticas completas
        """
        wallet = await self.get_or_create_wallet(guild_id)
        
        if not wallet:
            return {
                'balance_available': Decimal('0.00'),
                'balance_pending': Decimal('0.00'),
                'total_earned': Decimal('0.00'),
                'total_withdrawn': Decimal('0.00'),
                'platform_fees_paid': Decimal('0.00'),
                'net_profit': Decimal('0.00')
            }
        
        total_earned = Decimal(str(wallet.get('total_earned', 0)))
        total_withdrawn = Decimal(str(wallet.get('total_withdrawn', 0)))
        
        return {
            'balance_available': Decimal(str(wallet.get('balance_available', 0))),
            'balance_pending': Decimal(str(wallet.get('balance_pending', 0))),
            'total_earned': total_earned,
            'total_withdrawn': total_withdrawn,
            'platform_fees_paid': Decimal(str(wallet.get('platform_fees_paid', 0))),
            'net_profit': total_earned - total_withdrawn,
            'pix_key': wallet.get('pix_key'),
            'pix_type': wallet.get('pix_type')
        }
    
    async def save_pix_key(self, guild_id: int, pix_key: str, pix_type: str) -> bool:
        """
        Salva chave Pix padrão do servidor
        
        Args:
            guild_id: ID do servidor
            pix_key: Chave Pix
            pix_type: Tipo (cpf, cnpj, email, phone, random)
            
        Returns:
            True se sucesso
        """
        try:
            await self.get_or_create_wallet(guild_id)
            
            self.supabase.table('guild_wallets')\
                .update({
                    'pix_key': pix_key,
                    'pix_type': pix_type
                })\
                .eq('guild_id', guild_id)\
                .execute()
            
            print(f"🔑 Chave Pix salva para servidor {guild_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar chave Pix: {e}")
            return False

