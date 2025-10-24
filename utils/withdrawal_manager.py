"""
Gerenciador de Saques
Processa solicitações de saque via Pix automaticamente
"""

from supabase import create_client
from config.config import SUPABASE_URL, SUPABASE_KEY
from utils.mercadopago_manager import MercadoPagoManager
from models.wallet_model import WalletModel
from decimal import Decimal
from typing import Optional, Dict
from datetime import datetime
import re

class WithdrawalManager:
    """Gerencia solicitações de saque dos servidores"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.mp_manager = MercadoPagoManager()
        self.wallet_model = WalletModel()
    
    def validate_pix_key(self, pix_key: str, pix_type: str) -> tuple[bool, str]:
        """
        Valida formato da chave Pix
        
        Args:
            pix_key: Chave Pix
            pix_type: Tipo (cpf, cnpj, email, phone, random)
            
        Returns:
            Tuple (válido: bool, mensagem: str)
        """
        pix_key = pix_key.strip()
        
        if pix_type == 'cpf':
            # Remover formatação
            cpf = re.sub(r'[^0-9]', '', pix_key)
            if len(cpf) != 11:
                return False, "❌ CPF deve ter 11 dígitos"
            return True, cpf
            
        elif pix_type == 'cnpj':
            cnpj = re.sub(r'[^0-9]', '', pix_key)
            if len(cnpj) != 14:
                return False, "❌ CNPJ deve ter 14 dígitos"
            return True, cnpj
            
        elif pix_type == 'email':
            # Validação simples de email
            if '@' not in pix_key or '.' not in pix_key:
                return False, "❌ Email inválido"
            return True, pix_key.lower()
            
        elif pix_type == 'phone':
            # Formato: +5511999999999
            phone = re.sub(r'[^0-9+]', '', pix_key)
            if not phone.startswith('+') or len(phone) < 13:
                return False, "❌ Telefone deve estar no formato: +5511999999999"
            return True, phone
            
        elif pix_type == 'random':
            # Chave aleatória - geralmente UUID
            if len(pix_key) < 32:
                return False, "❌ Chave aleatória inválida"
            return True, pix_key
        
        return False, "❌ Tipo de chave Pix inválido"
    
    async def create_withdrawal_request(
        self,
        guild_id: int,
        user_id: int,
        amount: Decimal,
        pix_key: str,
        pix_type: str
    ) -> Optional[Dict]:
        """
        Cria solicitação de saque
        
        Args:
            guild_id: ID do servidor
            user_id: ID do usuário que solicitou
            amount: Valor a sacar
            pix_key: Chave Pix
            pix_type: Tipo da chave
            
        Returns:
            Dict com dados da solicitação ou None se erro
        """
        try:
            # 1. Validar chave Pix
            valid, result = self.validate_pix_key(pix_key, pix_type)
            if not valid:
                print(result)
                return None
            pix_key = result  # Chave normalizada
            
            # 2. Verificar se pode sacar
            can_withdraw, message = await self.wallet_model.can_withdraw(guild_id, amount)
            if not can_withdraw:
                print(message)
                return None
            
            # 3. Calcular taxas
            fees = await self.wallet_model.calculate_withdrawal_fees(amount)
            
            # 4. Criar solicitação no banco
            withdrawal_data = {
                'guild_id': guild_id,
                'user_id': user_id,
                'amount_requested': float(amount),
                'fee_amount': float(fees['fee_amount']),
                'net_amount': float(fees['net_amount']),
                'pix_key': pix_key,
                'pix_type': pix_type,
                'status': 'pending'
            }
            
            response = self.supabase.table('withdrawal_requests')\
                .insert(withdrawal_data)\
                .execute()
            
            if not response.data:
                print("❌ Erro ao criar solicitação de saque")
                return None
            
            withdrawal = response.data[0]
            
            print(f"📝 Solicitação de saque criada: #{withdrawal['id']} - R$ {amount:.2f}")
            
            return withdrawal
            
        except Exception as e:
            print(f"❌ Erro ao criar solicitação: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def process_withdrawal(self, withdrawal_id: int) -> bool:
        """
        Processa saque automaticamente via Mercado Pago
        
        Args:
            withdrawal_id: ID da solicitação
            
        Returns:
            True se processado com sucesso
        """
        try:
            # 1. Buscar solicitação
            response = self.supabase.table('withdrawal_requests')\
                .select('*')\
                .eq('id', withdrawal_id)\
                .execute()
            
            if not response.data:
                print(f"❌ Solicitação {withdrawal_id} não encontrada")
                return False
            
            withdrawal = response.data[0]
            
            # Verificar se já foi processada
            if withdrawal['status'] != 'pending':
                print(f"⚠️ Solicitação já processada: {withdrawal['status']}")
                return False
            
            # 2. Atualizar status para processing
            self.supabase.table('withdrawal_requests')\
                .update({'status': 'processing', 'processed_at': datetime.now().isoformat()})\
                .eq('id', withdrawal_id)\
                .execute()
            
            # 3. Debitar da carteira ANTES de enviar Pix
            guild_id = withdrawal['guild_id']
            amount = Decimal(str(withdrawal['amount_requested']))
            
            debit_success = await self.wallet_model.debit_wallet(guild_id, amount, withdrawal_id)
            
            if not debit_success:
                # Reverter status
                self.supabase.table('withdrawal_requests')\
                    .update({
                        'status': 'failed',
                        'error_message': 'Saldo insuficiente'
                    })\
                    .eq('id', withdrawal_id)\
                    .execute()
                return False
            
            # 4. Enviar Pix via Mercado Pago
            transfer = await self.mp_manager.send_pix(
                amount=float(withdrawal['net_amount']),
                pix_key=withdrawal['pix_key'],
                pix_type=withdrawal['pix_type'],
                description=f"Saque CaosBot #{withdrawal_id}"
            )
            
            if not transfer:
                # Falha ao enviar - reverter débito na carteira
                print("❌ Falha ao enviar Pix - revertendo saque")
                
                # TODO: Implementar função de reversão
                self.supabase.table('withdrawal_requests')\
                    .update({
                        'status': 'failed',
                        'error_message': 'Falha ao processar transferência Pix'
                    })\
                    .eq('id', withdrawal_id)\
                    .execute()
                
                return False
            
            # 5. Marcar como completed
            self.supabase.table('withdrawal_requests')\
                .update({
                    'status': 'completed',
                    'gateway_transaction_id': transfer.get('transfer_id'),
                    'completed_at': datetime.now().isoformat()
                })\
                .eq('id', withdrawal_id)\
                .execute()
            
            print(f"✅ Saque processado: #{withdrawal_id} - R$ {withdrawal['net_amount']:.2f} enviado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao processar saque: {e}")
            import traceback
            traceback.print_exc()
            
            # Marcar como failed
            self.supabase.table('withdrawal_requests')\
                .update({
                    'status': 'failed',
                    'error_message': str(e)
                })\
                .eq('id', withdrawal_id)\
                .execute()
            
            return False
    
    async def get_pending_withdrawals(self, guild_id: int = None) -> list:
        """
        Busca saques pendentes
        
        Args:
            guild_id: Filtrar por servidor (opcional)
            
        Returns:
            Lista de saques pendentes
        """
        try:
            query = self.supabase.table('withdrawal_requests')\
                .select('*')\
                .eq('status', 'pending')
            
            if guild_id:
                query = query.eq('guild_id', guild_id)
            
            response = query.order('requested_at', desc=False).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar saques pendentes: {e}")
            return []
    
    async def get_withdrawal_history(self, guild_id: int, limit: int = 20) -> list:
        """
        Busca histórico de saques de um servidor
        
        Args:
            guild_id: ID do servidor
            limit: Número de saques a retornar
            
        Returns:
            Lista de saques
        """
        try:
            response = self.supabase.table('withdrawal_requests')\
                .select('*')\
                .eq('guild_id', guild_id)\
                .order('requested_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    async def cancel_withdrawal(self, withdrawal_id: int, reason: str = "Cancelado pelo usuário") -> bool:
        """
        Cancela solicitação de saque pendente
        
        Args:
            withdrawal_id: ID da solicitação
            reason: Motivo do cancelamento
            
        Returns:
            True se cancelado
        """
        try:
            # Só pode cancelar se estiver pending
            response = self.supabase.table('withdrawal_requests')\
                .update({
                    'status': 'cancelled',
                    'error_message': reason
                })\
                .eq('id', withdrawal_id)\
                .eq('status', 'pending')\
                .execute()
            
            if response.data:
                print(f"🚫 Saque #{withdrawal_id} cancelado")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro ao cancelar saque: {e}")
            return False

