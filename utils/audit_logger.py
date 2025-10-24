"""
Sistema de Auditoria
Registra todas operações financeiras e ações administrativas
"""

from supabase import create_client
from config.config import Config
from typing import Optional, Dict, Any
from datetime import datetime
import json

class AuditLogger:
    """Logger de auditoria para operações financeiras"""
    
    def __init__(self):
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    async def log(
        self,
        guild_id: Optional[int],
        user_id: Optional[int],
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Registra ação de auditoria
        
        Args:
            guild_id: ID do servidor Discord
            user_id: ID do usuário que executou ação
            action: Nome da ação (credit_wallet, debit_wallet, etc)
            entity_type: Tipo de entidade afetada (wallet, transaction, etc)
            entity_id: ID da entidade
            old_value: Valor anterior (Dict/JSON)
            new_value: Novo valor (Dict/JSON)
            ip_address: IP do usuário (opcional)
            user_agent: User agent (opcional)
            
        Returns:
            True se sucesso
        """
        try:
            log_data = {
                'guild_id': guild_id,
                'user_id': user_id,
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'old_value': json.dumps(old_value) if old_value else None,
                'new_value': json.dumps(new_value) if new_value else None,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            
            self.supabase.table('audit_logs').insert(log_data).execute()
            
            print(f"📝 Audit Log: {action} por user {user_id} em guild {guild_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao registrar audit log: {e}")
            return False
    
    # ==============================================
    # LOGS ESPECÍFICOS - CARTEIRA
    # ==============================================
    
    async def log_wallet_credit(
        self,
        guild_id: int,
        transaction_id: int,
        amount: float,
        fee: float,
        net_amount: float,
        balance_after: float
    ) -> bool:
        """Registra crédito na carteira"""
        return await self.log(
            guild_id=guild_id,
            user_id=None,
            action='credit_wallet',
            entity_type='wallet',
            entity_id=guild_id,
            old_value=None,
            new_value={
                'transaction_id': transaction_id,
                'gross_amount': amount,
                'platform_fee': fee,
                'net_amount': net_amount,
                'balance_after': balance_after
            }
        )
    
    async def log_wallet_debit(
        self,
        guild_id: int,
        withdrawal_id: int,
        amount: float,
        fee: float,
        net_amount: float,
        balance_after: float
    ) -> bool:
        """Registra débito da carteira"""
        return await self.log(
            guild_id=guild_id,
            user_id=None,
            action='debit_wallet',
            entity_type='wallet',
            entity_id=guild_id,
            old_value=None,
            new_value={
                'withdrawal_id': withdrawal_id,
                'amount': amount,
                'fee': fee,
                'net_amount': net_amount,
                'balance_after': balance_after
            }
        )
    
    # ==============================================
    # LOGS ESPECÍFICOS - SAQUES
    # ==============================================
    
    async def log_withdrawal_request(
        self,
        guild_id: int,
        user_id: int,
        withdrawal_id: int,
        amount: float,
        pix_key: str,
        pix_type: str
    ) -> bool:
        """Registra solicitação de saque"""
        return await self.log(
            guild_id=guild_id,
            user_id=user_id,
            action='request_withdrawal',
            entity_type='withdrawal',
            entity_id=withdrawal_id,
            new_value={
                'amount': amount,
                'pix_type': pix_type,
                'pix_key_masked': f"{pix_key[:4]}***{pix_key[-4:]}"
            }
        )
    
    async def log_withdrawal_processed(
        self,
        guild_id: int,
        withdrawal_id: int,
        amount: float,
        gateway_tx_id: str,
        status: str
    ) -> bool:
        """Registra processamento de saque"""
        return await self.log(
            guild_id=guild_id,
            user_id=None,
            action='process_withdrawal',
            entity_type='withdrawal',
            entity_id=withdrawal_id,
            new_value={
                'amount': amount,
                'gateway_transaction_id': gateway_tx_id,
                'status': status
            }
        )
    
    async def log_withdrawal_failed(
        self,
        guild_id: int,
        withdrawal_id: int,
        error: str
    ) -> bool:
        """Registra falha no saque"""
        return await self.log(
            guild_id=guild_id,
            user_id=None,
            action='withdrawal_failed',
            entity_type='withdrawal',
            entity_id=withdrawal_id,
            new_value={
                'error': error
            }
        )
    
    # ==============================================
    # LOGS ESPECÍFICOS - PAGAMENTOS
    # ==============================================
    
    async def log_payment_created(
        self,
        guild_id: int,
        user_id: int,
        transaction_id: int,
        amount: float,
        gateway: str,
        payment_id: str
    ) -> bool:
        """Registra criação de pagamento"""
        return await self.log(
            guild_id=guild_id,
            user_id=user_id,
            action='create_payment',
            entity_type='transaction',
            entity_id=transaction_id,
            new_value={
                'amount': amount,
                'gateway': gateway,
                'payment_id': payment_id
            }
        )
    
    async def log_payment_approved(
        self,
        guild_id: int,
        transaction_id: int,
        payment_id: str,
        gateway: str
    ) -> bool:
        """Registra aprovação de pagamento"""
        return await self.log(
            guild_id=guild_id,
            user_id=None,
            action='payment_approved',
            entity_type='transaction',
            entity_id=transaction_id,
            new_value={
                'payment_id': payment_id,
                'gateway': gateway,
                'approved_at': datetime.now().isoformat()
            }
        )
    
    async def log_payment_failed(
        self,
        guild_id: int,
        transaction_id: int,
        reason: str
    ) -> bool:
        """Registra falha no pagamento"""
        return await self.log(
            guild_id=guild_id,
            user_id=None,
            action='payment_failed',
            entity_type='transaction',
            entity_id=transaction_id,
            new_value={
                'reason': reason,
                'failed_at': datetime.now().isoformat()
            }
        )
    
    # ==============================================
    # LOGS ESPECÍFICOS - CONFIGURAÇÕES
    # ==============================================
    
    async def log_config_change(
        self,
        guild_id: int,
        user_id: int,
        config_key: str,
        old_value: Any,
        new_value: Any
    ) -> bool:
        """Registra mudança de configuração"""
        return await self.log(
            guild_id=guild_id,
            user_id=user_id,
            action='change_config',
            entity_type='config',
            entity_id=guild_id,
            old_value={config_key: old_value},
            new_value={config_key: new_value}
        )
    
    async def log_gateway_switch(
        self,
        guild_id: int,
        user_id: int,
        old_gateway: str,
        new_gateway: str
    ) -> bool:
        """Registra mudança de gateway"""
        return await self.log_config_change(
            guild_id=guild_id,
            user_id=user_id,
            config_key='preferred_gateway',
            old_value=old_gateway,
            new_value=new_gateway
        )
    
    # ==============================================
    # QUERIES - BUSCAR LOGS
    # ==============================================
    
    async def get_logs(
        self,
        guild_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """
        Busca logs de auditoria com filtros
        
        Args:
            guild_id: Filtrar por servidor
            user_id: Filtrar por usuário
            action: Filtrar por ação
            limit: Limite de resultados
            
        Returns:
            Lista de logs
        """
        try:
            query = self.supabase.table('audit_logs').select('*')
            
            if guild_id:
                query = query.eq('guild_id', guild_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            if action:
                query = query.eq('action', action)
            
            response = query.order('created_at', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar logs: {e}")
            return []
    
    async def get_financial_summary(self, guild_id: int, days: int = 30) -> Dict:
        """
        Retorna resumo financeiro baseado nos logs
        
        Args:
            guild_id: ID do servidor
            days: Número de dias para análise
            
        Returns:
            Dict com estatísticas
        """
        try:
            # Buscar logs financeiros dos últimos X dias
            from datetime import datetime, timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            logs = await self.get_logs(guild_id=guild_id, limit=1000)
            
            # Filtrar logs recentes
            recent_logs = [
                log for log in logs
                if log.get('created_at', '') >= cutoff_date
            ]
            
            # Contar ações
            summary = {
                'total_credits': 0,
                'total_debits': 0,
                'total_withdrawals_requested': 0,
                'total_withdrawals_completed': 0,
                'total_payments_created': 0,
                'total_payments_approved': 0,
                'total_payments_failed': 0,
                'period_days': days
            }
            
            for log in recent_logs:
                action = log.get('action', '')
                
                if action == 'credit_wallet':
                    summary['total_credits'] += 1
                elif action == 'debit_wallet':
                    summary['total_debits'] += 1
                elif action == 'request_withdrawal':
                    summary['total_withdrawals_requested'] += 1
                elif action == 'process_withdrawal':
                    summary['total_withdrawals_completed'] += 1
                elif action == 'create_payment':
                    summary['total_payments_created'] += 1
                elif action == 'payment_approved':
                    summary['total_payments_approved'] += 1
                elif action == 'payment_failed':
                    summary['total_payments_failed'] += 1
            
            return summary
            
        except Exception as e:
            print(f"❌ Erro ao gerar resumo financeiro: {e}")
            return {}

