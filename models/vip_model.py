from supabase import create_client, Client
from config.config import Config
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class VipModel:
    """Modelo para gerenciamento de assinaturas VIP"""
    
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = 'vip_subscriptions'
    
    async def initialize(self):
        """Inicializa a tabela de assinaturas VIP"""
        try:
            result = self.supabase.table(self.table_name).select('*').limit(1).execute()
            print("✅ Tabela de assinaturas VIP conectada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao conectar com tabela de assinaturas VIP: {e}")
            print("💡 Execute o arquivo database_vip_setup.sql no Supabase para criar a tabela")
    
    async def create_subscription(
        self,
        user_id: int,
        guild_id: int,
        role_id: int,
        role_name: str,
        product_id: int,
        duration_days: Optional[int] = None,
        transaction_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Cria uma nova assinatura VIP
        
        Args:
            user_id: ID do usuário Discord
            guild_id: ID do servidor Discord
            role_id: ID da role VIP
            role_name: Nome da role VIP
            product_id: ID do produto VIP
            duration_days: Duração em dias (None = vitalício)
            transaction_id: ID da transação relacionada
        
        Returns:
            Dados da assinatura criada ou None em caso de erro
        """
        try:
            now = datetime.now()
            expires_at = None
            
            if duration_days is not None:
                expires_at = (now + timedelta(days=duration_days)).isoformat()
            
            subscription_data = {
                'user_id': user_id,
                'guild_id': guild_id,
                'role_id': role_id,
                'role_name': role_name,
                'product_id': product_id,
                'duration_days': duration_days,
                'started_at': now.isoformat(),
                'expires_at': expires_at,
                'status': 'active',
                'transaction_id': transaction_id
            }
            
            result = self.supabase.table(self.table_name).insert(subscription_data).execute()
            
            if result.data:
                print(f"✅ Assinatura VIP criada: {role_name} para usuário {user_id}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao criar assinatura VIP: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_user_subscription(self, user_id: int, guild_id: int) -> Optional[Dict]:
        """
        Busca a assinatura VIP ativa de um usuário em um servidor
        
        Args:
            user_id: ID do usuário
            guild_id: ID do servidor
        
        Returns:
            Dados da assinatura ativa ou None
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('guild_id', guild_id)\
                .eq('status', 'active')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar assinatura do usuário: {e}")
            return None
    
    async def get_all_subscriptions(self, guild_id: int, status: str = 'active') -> List[Dict]:
        """
        Busca todas as assinaturas de um servidor
        
        Args:
            guild_id: ID do servidor
            status: Status das assinaturas (active, expired, cancelled)
        
        Returns:
            Lista de assinaturas
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .eq('status', status)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar assinaturas: {e}")
            return []
    
    async def get_expiring_subscriptions(self, days: int = 3) -> List[Dict]:
        """
        Busca assinaturas que vão expirar nos próximos X dias
        
        Args:
            days: Número de dias para o aviso (padrão: 3)
        
        Returns:
            Lista de assinaturas próximas de expirar
        """
        try:
            future_date = (datetime.now() + timedelta(days=days)).isoformat()
            now = datetime.now().isoformat()
            
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('status', 'active')\
                .not_.is_('expires_at', 'null')\
                .gte('expires_at', now)\
                .lte('expires_at', future_date)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar assinaturas próximas de expirar: {e}")
            return []
    
    async def check_and_expire_subscriptions(self) -> List[Dict]:
        """
        Verifica e expira assinaturas vencidas
        
        Returns:
            Lista de assinaturas que foram expiradas
        """
        try:
            now = datetime.now().isoformat()
            
            # Buscar assinaturas expiradas
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('status', 'active')\
                .not_.is_('expires_at', 'null')\
                .lte('expires_at', now)\
                .execute()
            
            expired_subscriptions = result.data if result.data else []
            
            # Marcar como expiradas
            for subscription in expired_subscriptions:
                await self.expire_subscription(subscription['id'])
            
            if expired_subscriptions:
                print(f"⏰ {len(expired_subscriptions)} assinatura(s) VIP expirada(s)")
            
            return expired_subscriptions
            
        except Exception as e:
            print(f"❌ Erro ao verificar assinaturas expiradas: {e}")
            return []
    
    async def expire_subscription(self, subscription_id: int) -> bool:
        """
        Marca uma assinatura como expirada
        
        Args:
            subscription_id: ID da assinatura
        
        Returns:
            True se foi expirada com sucesso
        """
        try:
            result = self.supabase.table(self.table_name)\
                .update({'status': 'expired'})\
                .eq('id', subscription_id)\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"❌ Erro ao expirar assinatura: {e}")
            return False
    
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """
        Cancela uma assinatura VIP
        
        Args:
            subscription_id: ID da assinatura
        
        Returns:
            True se foi cancelada com sucesso
        """
        try:
            result = self.supabase.table(self.table_name)\
                .update({'status': 'cancelled'})\
                .eq('id', subscription_id)\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"❌ Erro ao cancelar assinatura: {e}")
            return False
    
    async def get_subscription_history(self, user_id: int, guild_id: int) -> List[Dict]:
        """
        Busca o histórico de assinaturas de um usuário
        
        Args:
            user_id: ID do usuário
            guild_id: ID do servidor
        
        Returns:
            Lista de assinaturas (ativas, expiradas e canceladas)
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('guild_id', guild_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar histórico de assinaturas: {e}")
            return []
    
    async def get_subscription_by_id(self, subscription_id: int) -> Optional[Dict]:
        """
        Busca uma assinatura por ID
        
        Args:
            subscription_id: ID da assinatura
        
        Returns:
            Dados da assinatura ou None
        """
        try:
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('id', subscription_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar assinatura por ID: {e}")
            return None
    
    async def get_vip_stats(self, guild_id: int) -> Dict:
        """
        Retorna estatísticas das assinaturas VIP de um servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Total de assinaturas ativas
            active_result = self.supabase.table(self.table_name)\
                .select('id', count='exact')\
                .eq('guild_id', guild_id)\
                .eq('status', 'active')\
                .execute()
            
            # Total de assinaturas expiradas
            expired_result = self.supabase.table(self.table_name)\
                .select('id', count='exact')\
                .eq('guild_id', guild_id)\
                .eq('status', 'expired')\
                .execute()
            
            # Assinaturas por role
            all_active = await self.get_all_subscriptions(guild_id, 'active')
            by_role = {}
            vitalicio_count = 0
            
            for sub in all_active:
                role_name = sub['role_name']
                by_role[role_name] = by_role.get(role_name, 0) + 1
                
                if sub['duration_days'] is None:
                    vitalicio_count += 1
            
            return {
                'total_active': active_result.count if active_result.count else 0,
                'total_expired': expired_result.count if expired_result.count else 0,
                'vitalicio_count': vitalicio_count,
                'by_role': by_role
            }
            
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas VIP: {e}")
            return {
                'total_active': 0,
                'total_expired': 0,
                'vitalicio_count': 0,
                'by_role': {}
            }
    
    async def has_warned_expiration(self, subscription_id: int) -> bool:
        """
        Verifica se já foi enviado aviso de expiração
        Para evitar spam, podemos adicionar um campo 'warned' na tabela
        Por enquanto, retorna False (sempre avisa)
        
        Args:
            subscription_id: ID da assinatura
        
        Returns:
            True se já foi avisado
        """
        # TODO: Implementar lógica de controle de avisos enviados
        # Pode adicionar campo 'expiration_warned' BOOLEAN na tabela
        return False


