from supabase import create_client, Client
from config.config import Config
from typing import List, Dict, Optional
from datetime import datetime

class TransactionModel:
    """Modelo para interações com transações no banco de dados"""
    
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = 'transactions'
    
    async def initialize(self):
        """Inicializa a tabela de transações se não existir"""
        try:
            # Verificar se a tabela existe
            result = self.supabase.table(self.table_name).select('*').limit(1).execute()
            print("✅ Tabela de transações conectada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao conectar com tabela de transações: {e}")
            # Em produção, você criaria a tabela aqui
            print("💡 Crie a tabela 'transactions' no Supabase com os campos: id, user_id, product_id, amount, status, email, payment_id, pix_code, qr_code, created_at, updated_at")
    
    async def create_transaction(self, user_id: int, product_id: int, amount: float, status: str = 'pending', **kwargs) -> Dict:
        """Cria uma nova transação"""
        try:
            transaction_data = {
                'user_id': user_id,
                'product_id': product_id,
                'amount': amount,
                'status': status,
                'created_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.supabase.table(self.table_name).insert(transaction_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar transação: {e}")
            return None
    
    async def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        """Busca uma transação por ID"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('id', transaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar transação: {e}")
            return None
    
    async def get_user_transactions(self, user_id: int) -> List[Dict]:
        """Busca todas as transações de um usuário"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar transações do usuário: {e}")
            return []
    
    async def get_transactions_by_status(self, status: str) -> List[Dict]:
        """Busca transações por status"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('status', status).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar transações por status: {e}")
            return []
    
    async def update_transaction(self, transaction_id: int, update_data: Dict) -> Optional[Dict]:
        """Atualiza uma transação"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            result = self.supabase.table(self.table_name).update(update_data).eq('id', transaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao atualizar transação: {e}")
            return None
    
    async def delete_transaction(self, transaction_id: int) -> bool:
        """Deleta uma transação"""
        try:
            result = self.supabase.table(self.table_name).delete().eq('id', transaction_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar transação: {e}")
            return False
    
    async def get_transaction_with_product(self, transaction_id: int) -> Optional[Dict]:
        """Busca uma transação com informações do produto"""
        try:
            result = self.supabase.table(self.table_name).select('*, products(*)').eq('id', transaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar transação com produto: {e}")
            return None
    
    async def get_user_transactions_with_products(self, user_id: int) -> List[Dict]:
        """Busca transações do usuário com informações dos produtos"""
        try:
            result = self.supabase.table(self.table_name).select('*, products(*)').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar transações do usuário com produtos: {e}")
            return []
    
    async def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Busca transações por período"""
        try:
            result = self.supabase.table(self.table_name).select('*').gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat()).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar transações por período: {e}")
            return []
    
    async def get_transaction_stats(self) -> Dict:
        """Retorna estatísticas das transações"""
        try:
            # Total de transações
            total_result = self.supabase.table(self.table_name).select('id', count='exact').execute()
            total_transactions = total_result.count if total_result.count else 0
            
            # Transações por status
            pending_result = self.supabase.table(self.table_name).select('id', count='exact').eq('status', 'pending').execute()
            approved_result = self.supabase.table(self.table_name).select('id', count='exact').eq('status', 'approved').execute()
            failed_result = self.supabase.table(self.table_name).select('id', count='exact').eq('status', 'failed').execute()
            
            # Valor total das transações aprovadas
            revenue_result = self.supabase.table(self.table_name).select('amount').eq('status', 'approved').execute()
            total_revenue = sum(transaction['amount'] for transaction in revenue_result.data) if revenue_result.data else 0
            
            return {
                'total_transactions': total_transactions,
                'pending': pending_result.count if pending_result.count else 0,
                'approved': approved_result.count if approved_result.count else 0,
                'failed': failed_result.count if failed_result.count else 0,
                'total_revenue': total_revenue
            }
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return {}
