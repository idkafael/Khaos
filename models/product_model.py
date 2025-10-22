from supabase import create_client, Client
from config.config import Config
from typing import List, Dict, Optional
import asyncio

class ProductModel:
    """Modelo para interações com produtos no banco de dados - MULTI-SERVIDOR"""
    
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
            print("💡 Execute database_multiserver_setup.sql no Supabase")
    
    async def create_product(self, guild_id: int, product_data: Dict) -> Dict:
        """
        Cria um novo produto no banco de dados
        
        Args:
            guild_id: ID do servidor Discord
            product_data: Dados do produto
        
        Returns:
            Produto criado ou None
        """
        try:
            product_data['guild_id'] = guild_id
            result = self.supabase.table(self.table_name).insert(product_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao criar produto: {e}")
            return None
    
    async def get_products_by_guild(self, guild_id: int) -> List[Dict]:
        """
        Retorna todos os produtos de um servidor
        
        Args:
            guild_id: ID do servidor Discord
        
        Returns:
            Lista de produtos do servidor
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .order('created_at', desc=True)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos do servidor: {e}")
            return []
    
    async def get_all_products(self, guild_id: int = None) -> List[Dict]:
        """
        Retorna todos os produtos (com filtro opcional por servidor)
        
        Args:
            guild_id: ID do servidor (opcional)
        
        Returns:
            Lista de produtos
        """
        if guild_id:
            return await self.get_products_by_guild(guild_id)
        
        try:
            result = self.supabase.table(self.table_name).select('*').order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
    
    async def get_product_by_id(self, product_id: int, guild_id: int = None) -> Optional[Dict]:
        """
        Busca um produto por ID (com validação opcional de servidor)
        
        Args:
            product_id: ID do produto
            guild_id: ID do servidor (para validação)
        
        Returns:
            Produto ou None
        """
        try:
            query = self.supabase.table(self.table_name).select('*').eq('id', product_id)
            
            if guild_id:
                query = query.eq('guild_id', guild_id)
            
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar produto por ID: {e}")
            return None
    
    async def get_product_by_name(self, name: str, guild_id: int) -> Optional[Dict]:
        """
        Busca um produto por nome em um servidor
        
        Args:
            name: Nome do produto
            guild_id: ID do servidor
        
        Returns:
            Produto ou None
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .ilike('name', f'%{name}%')\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar produto por nome: {e}")
            return None
    
    async def search_products(self, search_term: str, guild_id: int) -> List[Dict]:
        """
        Busca produtos por nome ou descrição em um servidor
        
        Args:
            search_term: Termo de busca
            guild_id: ID do servidor
        
        Returns:
            Lista de produtos encontrados
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .or_(f'name.ilike.%{search_term}%,description.ilike.%{search_term}%')\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
    
    async def update_product(self, product_id: int, guild_id: int, update_data: Dict) -> Optional[Dict]:
        """
        Atualiza um produto (apenas se pertencer ao servidor)
        
        Args:
            product_id: ID do produto
            guild_id: ID do servidor
            update_data: Dados para atualizar
        
        Returns:
            Produto atualizado ou None
        """
        try:
            result = self.supabase.table(self.table_name)\
                .update(update_data)\
                .eq('id', product_id)\
                .eq('guild_id', guild_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            return None
    
    async def delete_product(self, product_id: int, guild_id: int) -> bool:
        """
        Deleta um produto (apenas se pertencer ao servidor)
        
        Args:
            product_id: ID do produto
            guild_id: ID do servidor
        
        Returns:
            True se deletou com sucesso
        """
        try:
            # Primeiro verifica se o produto existe
            product = await self.get_product_by_id(product_id, guild_id)
            if not product:
                print(f"Produto {product_id} não encontrado no servidor {guild_id}")
                return False
            
            # Deleta o produto
            result = self.supabase.table(self.table_name)\
                .delete()\
                .eq('id', product_id)\
                .eq('guild_id', guild_id)\
                .execute()
            
            print(f"✅ Produto {product_id} deletado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar produto {product_id}: {e}")
            return False
    
    async def get_products_by_category(self, category: str, guild_id: int) -> List[Dict]:
        """
        Busca produtos por categoria em um servidor
        
        Args:
            category: Categoria do produto
            guild_id: ID do servidor
        
        Returns:
            Lista de produtos da categoria
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .eq('category', category)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos por categoria: {e}")
            return []
    
    async def get_products_by_price_range(self, min_price: float, max_price: float, guild_id: int) -> List[Dict]:
        """
        Busca produtos por faixa de preço em um servidor
        
        Args:
            min_price: Preço mínimo
            max_price: Preço máximo
            guild_id: ID do servidor
        
        Returns:
            Lista de produtos na faixa de preço
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .gte('price', min_price)\
                .lte('price', max_price)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Erro ao buscar produtos por faixa de preço: {e}")
            return []
