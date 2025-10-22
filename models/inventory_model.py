from supabase import create_client, Client
from config.config import Config
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class InventoryModel:
    """Modelo para gestão de estoque de produtos digitais"""
    
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = 'product_inventory'
    
    async def initialize(self):
        """Inicializa a tabela de estoque"""
        try:
            result = self.supabase.table(self.table_name).select('*').limit(1).execute()
            print("✅ Tabela de estoque conectada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao conectar com tabela de estoque: {e}")
            print("💡 Execute o SQL de criação da tabela product_inventory no Supabase")
    
    async def add_stock(self, product_id: int, guild_id: int, content: str) -> Optional[Dict]:
        """Adiciona um item ao estoque"""
        try:
            stock_data = {
                'product_id': product_id,
                'guild_id': guild_id,
                'content': content,
                'status': 'available',
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name).insert(stock_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao adicionar estoque: {e}")
            return None
    
    async def add_bulk_stock(self, product_id: int, guild_id: int, contents: List[str]) -> int:
        """Adiciona múltiplos itens ao estoque de uma vez"""
        try:
            stock_items = [
                {
                    'product_id': product_id,
                    'guild_id': guild_id,
                    'content': content.strip(),
                    'status': 'available',
                    'created_at': datetime.now().isoformat()
                }
                for content in contents if content.strip()
            ]
            
            if not stock_items:
                return 0
            
            result = self.supabase.table(self.table_name).insert(stock_items).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Erro ao adicionar estoque em massa: {e}")
            return 0
    
    async def get_available_stock(self, product_id: int, guild_id: int) -> Optional[Dict]:
        """Retorna o primeiro item disponível do estoque"""
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('product_id', product_id)\
                .eq('guild_id', guild_id)\
                .eq('status', 'available')\
                .order('created_at')\
                .limit(1)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar estoque disponível: {e}")
            return None
    
    async def reserve_stock(self, inventory_id: int, user_id: int, transaction_id: int) -> bool:
        """Reserva um item do estoque"""
        try:
            update_data = {
                'status': 'reserved',
                'sold_to_user_id': user_id,
                'transaction_id': transaction_id,
                'reserved_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name).update(update_data).eq('id', inventory_id).eq('status', 'available').execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Erro ao reservar estoque: {e}")
            return False
    
    async def mark_as_sold(self, inventory_id: int) -> bool:
        """Marca um item como vendido"""
        try:
            update_data = {
                'status': 'sold',
                'sold_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name).update(update_data).eq('id', inventory_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Erro ao marcar estoque como vendido: {e}")
            return False
    
    async def release_reservation(self, inventory_id: int) -> bool:
        """Libera uma reserva, voltando o item para disponível"""
        try:
            update_data = {
                'status': 'available',
                'sold_to_user_id': None,
                'transaction_id': None,
                'reserved_at': None,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name).update(update_data).eq('id', inventory_id).eq('status', 'reserved').execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            print(f"Erro ao liberar reserva: {e}")
            return False
    
    async def release_expired_reservations(self) -> int:
        """Libera reservas expiradas (>10 minutos)"""
        try:
            expiration_time = (datetime.now() - timedelta(minutes=10)).isoformat()
            
            # Buscar reservas expiradas
            expired = self.supabase.table(self.table_name).select('id').eq('status', 'reserved').lt('reserved_at', expiration_time).execute()
            
            if not expired.data:
                return 0
            
            # Liberar todas de uma vez
            update_data = {
                'status': 'available',
                'sold_to_user_id': None,
                'transaction_id': None,
                'reserved_at': None,
                'updated_at': datetime.now().isoformat()
            }
            
            expired_ids = [item['id'] for item in expired.data]
            result = self.supabase.table(self.table_name).update(update_data).in_('id', expired_ids).execute()
            
            count = len(result.data) if result.data else 0
            if count > 0:
                print(f"🔄 {count} reservas expiradas foram liberadas")
            return count
        except Exception as e:
            print(f"Erro ao liberar reservas expiradas: {e}")
            return 0
    
    async def get_stock_count(self, product_id: int) -> Dict[str, int]:
        """Retorna contagem de estoque por status"""
        try:
            # Total disponível
            available = self.supabase.table(self.table_name).select('id', count='exact').eq('product_id', product_id).eq('status', 'available').execute()
            
            # Total reservado
            reserved = self.supabase.table(self.table_name).select('id', count='exact').eq('product_id', product_id).eq('status', 'reserved').execute()
            
            # Total vendido
            sold = self.supabase.table(self.table_name).select('id', count='exact').eq('product_id', product_id).eq('status', 'sold').execute()
            
            return {
                'available': available.count if available.count else 0,
                'reserved': reserved.count if reserved.count else 0,
                'sold': sold.count if sold.count else 0,
                'total': (available.count or 0) + (reserved.count or 0) + (sold.count or 0)
            }
        except Exception as e:
            print(f"Erro ao contar estoque: {e}")
            return {'available': 0, 'reserved': 0, 'sold': 0, 'total': 0}
    
    async def get_all_stock_summary(self) -> List[Dict]:
        """Retorna resumo de estoque de todos os produtos"""
        try:
            # Buscar todos os produtos únicos
            products = self.supabase.table('products').select('id, name, category').execute()
            
            if not products.data:
                return []
            
            summary = []
            for product in products.data:
                counts = await self.get_stock_count(product['id'])
                summary.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'category': product.get('category', 'Sem categoria'),
                    **counts
                })
            
            return summary
        except Exception as e:
            print(f"Erro ao buscar resumo de estoque: {e}")
            return []
    
    async def get_inventory_by_transaction(self, transaction_id: int) -> Optional[Dict]:
        """Busca item do estoque por ID da transação"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('transaction_id', transaction_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar estoque por transação: {e}")
            return None

