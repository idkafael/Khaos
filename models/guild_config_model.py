from supabase import create_client, Client
from config.config import Config
from typing import Optional, Dict, List
from datetime import datetime

class GuildConfigModel:
    """Modelo para gerenciar configurações por servidor Discord"""
    
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = 'guild_config'
    
    async def initialize(self):
        """Inicializa a tabela de configuração de servidores"""
        try:
            result = self.supabase.table(self.table_name).select('*').limit(1).execute()
            print("✅ Tabela de configuração de servidores conectada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao conectar com tabela guild_config: {e}")
            print("💡 Execute o arquivo database_multiserver_setup.sql no Supabase")
    
    async def get_config(self, guild_id: int) -> Optional[Dict]:
        """
        Busca a configuração de um servidor
        
        Args:
            guild_id: ID do servidor Discord
        
        Returns:
            Configuração do servidor ou None
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar configuração do servidor {guild_id}: {e}")
            return None
    
    async def create_or_update_config(
        self,
        guild_id: int,
        guild_name: str = None,
        **config_data
    ) -> Optional[Dict]:
        """
        Cria ou atualiza configuração de um servidor
        
        Args:
            guild_id: ID do servidor
            guild_name: Nome do servidor
            **config_data: Dados de configuração (pushinpay_api_key, split_percent, etc)
        
        Returns:
            Configuração salva ou None em caso de erro
        """
        try:
            # Verificar se já existe
            existing = await self.get_config(guild_id)
            
            config = {
                'guild_id': guild_id,
                'guild_name': guild_name,
                **config_data
            }
            
            if existing:
                # Atualizar
                result = self.supabase.table(self.table_name)\
                    .update(config)\
                    .eq('guild_id', guild_id)\
                    .execute()
            else:
                # Criar
                result = self.supabase.table(self.table_name)\
                    .insert(config)\
                    .execute()
            
            if result.data:
                print(f"✅ Configuração salva para servidor {guild_id}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao salvar configuração do servidor: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_pushinpay_key(self, guild_id: int) -> str:
        """
        Retorna a API Key do PushinPay para o servidor
        Se o servidor não tiver key própria, retorna a global
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            API Key do PushinPay
        """
        config = await self.get_config(guild_id)
        
        if config and config.get('pushinpay_api_key'):
            return config['pushinpay_api_key']
        
        # Retornar key global
        return Config.PUSHINPAY_API_KEY
    
    async def get_split_config(self, guild_id: int) -> Optional[Dict]:
        """
        Retorna configuração de split de pagamento
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            Dict com recipient_id e percent, ou None se não configurado
        """
        config = await self.get_config(guild_id)
        
        if not config:
            return None
        
        split_percent = config.get('pushinpay_split_percent', 0)
        split_recipient = config.get('pushinpay_split_recipient_id')
        
        if split_percent > 0 and split_recipient:
            return {
                'recipient_id': split_recipient,
                'percent': float(split_percent)
            }
        
        return None
    
    async def get_admin_role_ids(self, guild_id: int) -> List[int]:
        """
        Retorna lista de IDs de roles admin do servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            Lista de IDs de roles
        """
        config = await self.get_config(guild_id)
        
        if config and config.get('admin_role_ids'):
            return config['admin_role_ids']
        
        return []
    
    async def set_admin_roles(self, guild_id: int, role_ids: List[int]) -> bool:
        """
        Define roles admin do servidor
        
        Args:
            guild_id: ID do servidor
            role_ids: Lista de IDs de roles
        
        Returns:
            True se salvou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                admin_role_ids=role_ids
            )
            return result is not None
        except Exception as e:
            print(f"❌ Erro ao definir roles admin: {e}")
            return False
    
    async def set_ticket_config(
        self,
        guild_id: int,
        category_id: Optional[int] = None,
        logs_channel_id: Optional[int] = None
    ) -> bool:
        """
        Define configuração de tickets do servidor
        
        Args:
            guild_id: ID do servidor
            category_id: ID da categoria de tickets
            logs_channel_id: ID do canal de logs
        
        Returns:
            True se salvou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                ticket_category_id=category_id,
                ticket_logs_channel_id=logs_channel_id
            )
            return result is not None
        except Exception as e:
            print(f"❌ Erro ao definir configuração de tickets: {e}")
            return False
    
    async def is_active(self, guild_id: int) -> bool:
        """
        Verifica se o servidor está ativo
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            True se ativo
        """
        config = await self.get_config(guild_id)
        
        if not config:
            return True  # Se não tem config, considera ativo
        
        return config.get('is_active', True)
    
    async def deactivate_guild(self, guild_id: int) -> bool:
        """
        Desativa um servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            True se desativou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                is_active=False
            )
            return result is not None
        except Exception as e:
            print(f"❌ Erro ao desativar servidor: {e}")
            return False
    
    async def set_ticket_product_filter(
        self,
        guild_id: int,
        product_ids: Optional[List[int]] = None
    ) -> bool:
        """
        Define filtro de produtos para tickets de compra
        
        Args:
            guild_id: ID do servidor
            product_ids: Lista de IDs de produtos permitidos (None = todos)
        
        Returns:
            True se salvou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                ticket_allowed_products=product_ids
            )
            return result is not None
        except Exception as e:
            print(f"❌ Erro ao definir filtro de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_allowed_products(self, guild_id: int) -> Optional[List[int]]:
        """
        Retorna lista de IDs de produtos permitidos no ticket
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            Lista de IDs permitidos ou None (todos produtos)
        """
        config = await self.get_config(guild_id)
        
        if not config:
            return None  # Todos produtos disponíveis
        
        return config.get('ticket_allowed_products')
    
    async def set_log_config(
        self,
        guild_id: int,
        log_channel_id: int,
        log_events: Optional[List[str]] = None
    ) -> bool:
        """
        Define configuração de logs do servidor
        
        Args:
            guild_id: ID do servidor
            log_channel_id: ID do canal de logs
            log_events: Lista de eventos para logar (None = todos)
        
        Returns:
            True se salvou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                log_channel_id=log_channel_id,
                log_events=log_events
            )
            return result is not None
        except Exception as e:
            print(f"❌ Erro ao definir configuração de logs: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_log_config(self, guild_id: int) -> Optional[Dict]:
        """
        Retorna configuração de logs do servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            Dict com log_channel_id e log_events ou None
        """
        config = await self.get_config(guild_id)
        
        if not config or not config.get('log_channel_id'):
            return None
        
        return {
            'log_channel_id': config.get('log_channel_id'),
            'log_events': config.get('log_events', [])  # Array de eventos
        }
    
    async def disable_logs(self, guild_id: int) -> bool:
        """
        Desabilita logs do servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            True se desabilitou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                log_channel_id=None,
                log_level=None
            )
            return result is not None
        except Exception as e:
            print(f"❌ Erro ao desabilitar logs: {e}")
            return False

