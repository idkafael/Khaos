from supabase import create_client, Client
from config.config import Config
from typing import List, Dict, Optional
import asyncio

class ProductModel:
    """Modelo para interações com produtos no banco de dados"""
    
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = 'products'
    
    async def initialize(self):
        """Inicializa a tabela de produtos se não existir"""
        try:
            # Verificar se a tabela existe
            result = self.supabase.table(self.table_name).select('*').limit(1).execute()
            print("✅ Tabela de produtos conectada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao conectar com tabela de produtos: {e}")
            # Em produção, você criaria a tabela aqui
            print("💡 Crie a tabela 'products' no Supabase com os campos: id, name, description, price, category, created_at, updated_at")
    
    async def create_product(self, product_data: Dict) -> Dict:
        """Cria um novo produto no banco de dados"""
        try:
            result = self.supabase.table(self.table_name).insert(product_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar produto: {e}")
            return None
    
    async def get_all_products(self) -> List[Dict]:
        """Retorna todos os produtos"""
        try:
            result = self.supabase.table(self.table_name).select('*').order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
    
    async def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Busca um produto por ID"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('id', product_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar produto por ID: {e}")
            return None
    
    async def get_product_by_name(self, name: str) -> Optional[Dict]:
        """Busca um produto por nome"""
        try:
            result = self.supabase.table(self.table_name).select('*').ilike('name', f'%{name}%').execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar produto por nome: {e}")
            return None
    
    async def search_products(self, search_term: str) -> List[Dict]:
        """Busca produtos por nome ou descrição"""
        try:
            result = self.supabase.table(self.table_name).select('*').or_(
                f'name.ilike.%{search_term}%,description.ilike.%{search_term}%'
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
    
    async def update_product(self, product_id: int, update_data: Dict) -> Optional[Dict]:
        """Atualiza um produto"""
        try:
            result = self.supabase.table(self.table_name).update(update_data).eq('id', product_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            return None
    
    async def delete_product(self, product_id: int) -> bool:
        """Deleta um produto"""
        try:
            result = self.supabase.table(self.table_name).delete().eq('id', product_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar produto: {e}")
            return False
    
    async def get_products_by_category(self, category: str) -> List[Dict]:
        """Busca produtos por categoria"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('category', category).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos por categoria: {e}")
            return []
    
    async def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """Busca produtos por faixa de preço"""
        try:
            result = self.supabase.table(self.table_name).select('*').gte('price', min_price).lte('price', max_price).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos por faixa de preço: {e}")
            return []
