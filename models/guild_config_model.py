from supabase import create_client, Client
from config.config import Config
from typing import Optional, Dict, List
from datetime import datetime

class GuildConfigModel:
    """Modelo para gerenciar configurações por servidor Discord"""
    
    def __init__(self):
        print(f"[CONFIG] [GuildConfigModel] Inicializando...")
        print(f"[CONFIG] [GuildConfigModel] SUPABASE_URL: {Config.SUPABASE_URL[:20]}...")
        print(f"[CONFIG] [GuildConfigModel] SUPABASE_KEY: {Config.SUPABASE_KEY[:20]}...")
        try:
            self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            print(f"[OK] [GuildConfigModel] Supabase client criado com sucesso")
            self.table_name = 'guild_config'
            print(f"[OK] [GuildConfigModel] Table name: {self.table_name}")
        except Exception as e:
            print(f"[ERROR] [GuildConfigModel] Erro ao criar Supabase client: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def initialize(self):
        """Inicializa a tabela de configuração de servidores"""
        try:
            result = self.supabase.table(self.table_name).select('*').limit(1).execute()
            print("[OK] Tabela de configuração de servidores conectada com sucesso")
        except Exception as e:
            print(f"[ERROR] Erro ao conectar com tabela guild_config: {e}")
            print("💡 Execute o arquivo database_multiserver_setup.sql no Supabase")
    
    async def get_config(self, guild_id: int) -> Optional[Dict]:
        """
        Busca a configuração de um servidor

        Args:
            guild_id: ID do servidor Discord

        Returns:
            Configuração do servidor ou None
        """
        print(f"[CONFIG] [GuildConfigModel] get_config chamado para guild_id: {guild_id}")

        try:
            print(f"[CONFIG] [GuildConfigModel] Executando query SELECT...")
            result = self.supabase.table(self.table_name)\
                .select('*')\
                .eq('guild_id', guild_id)\
                .execute()

            print(f"[CONFIG] [GuildConfigModel] Query result: {result}")
            print(f"[CONFIG] [GuildConfigModel] Result data: {result.data}")
            print(f"[CONFIG] [GuildConfigModel] Result data length: {len(result.data) if result.data else 0}")

            if result.data:
                print(f"[CONFIG] [GuildConfigModel] Config encontrada: {result.data[0]}")
                return result.data[0]
            else:
                print(f"[CONFIG] [GuildConfigModel] Nenhuma config encontrada para guild {guild_id}")
                return None

        except Exception as e:
            print(f"[ERROR] [GuildConfigModel] Erro ao buscar configuração do servidor {guild_id}: {e}")
            import traceback
            traceback.print_exc()
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
        print(f"[CONFIG] [GuildConfigModel] create_or_update_config chamado")
        print(f"[CONFIG] [GuildConfigModel] guild_id: {guild_id}")
        print(f"[CONFIG] [GuildConfigModel] guild_name: {guild_name}")
        print(f"[CONFIG] [GuildConfigModel] config_data: {config_data}")

        try:
            # Verificar se já existe
            print(f"[CONFIG] [GuildConfigModel] Verificando se config já existe...")
            existing = await self.get_config(guild_id)
            print(f"[CONFIG] [GuildConfigModel] Config existente: {existing is not None}")

            config = {
                'guild_id': guild_id,
                'guild_name': guild_name,
                **config_data
            }
            print(f"[CONFIG] [GuildConfigModel] Config final: {config}")

            if existing:
                # Atualizar
                print(f"[CONFIG] [GuildConfigModel] Atualizando configuração existente...")
                result = self.supabase.table(self.table_name)\
                    .update(config)\
                    .eq('guild_id', guild_id)\
                    .execute()
                print(f"[CONFIG] [GuildConfigModel] Update result: {result}")
            else:
                # Criar
                print(f"[CONFIG] [GuildConfigModel] Criando nova configuração...")
                result = self.supabase.table(self.table_name)\
                    .insert(config)\
                    .execute()
                print(f"[CONFIG] [GuildConfigModel] Insert result: {result}")

            print(f"[CONFIG] [GuildConfigModel] Result data: {result.data}")
            print(f"[CONFIG] [GuildConfigModel] Result data length: {len(result.data) if result.data else 0}")

            if result.data:
                print(f"[OK] [GuildConfigModel] Configuração salva para servidor {guild_id}")
                print(f"[OK] [GuildConfigModel] Data returned: {result.data[0]}")
                return result.data[0]
            else:
                print(f"⚠️ [GuildConfigModel] Nenhum dado retornado do banco")
                print(f"⚠️ [GuildConfigModel] Result: {result}")
                return None

        except Exception as e:
            print(f"[ERROR] [GuildConfigModel] Erro ao salvar configuração do servidor: {e}")
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
            print(f"[ERROR] Erro ao definir roles admin: {e}")
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
            print(f"[ERROR] Erro ao definir configuração de tickets: {e}")
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
            print(f"[ERROR] Erro ao desativar servidor: {e}")
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
        print(f"[CONFIG] [GuildConfigModel] set_ticket_product_filter chamado")
        print(f"[CONFIG] [GuildConfigModel] guild_id: {guild_id}")
        print(f"[CONFIG] [GuildConfigModel] product_ids: {product_ids}")

        try:
            print(f"[CONFIG] [GuildConfigModel] Chamando create_or_update_config...")

            # Primeiro, verificar se a coluna ticket_allowed_products existe
            print(f"[CONFIG] [GuildConfigModel] Verificando se coluna ticket_allowed_products existe...")
            try:
                # Tentar fazer uma query que use a coluna
                test_result = self.supabase.table(self.table_name).select('ticket_allowed_products').limit(1).execute()
                print(f"[OK] Coluna ticket_allowed_products existe no banco")
            except Exception as e:
                print(f"[ERROR] Coluna ticket_allowed_products NÃO existe no banco!")
                print(f"[ERROR] Erro: {e}")
                print(f"💡 Execute: ALTER TABLE guild_config ADD COLUMN IF NOT EXISTS ticket_allowed_products INTEGER[];")
                return False

            result = await self.create_or_update_config(
                guild_id=guild_id,
                ticket_allowed_products=product_ids
            )
            print(f"[CONFIG] [GuildConfigModel] Resultado: {result}")
            return result is not None
        except Exception as e:
            print(f"[ERROR] [GuildConfigModel] Erro ao definir filtro de produtos: {e}")
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
            print(f"[ERROR] Erro ao definir configuração de logs: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def set_feedback_channel(self, guild_id: int, feedback_channel_id: int) -> bool:
        """
        Define o canal de feedback do servidor
        
        Args:
            guild_id: ID do servidor
            feedback_channel_id: ID do canal de feedback
        
        Returns:
            True se salvou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                feedback_channel_id=feedback_channel_id
            )
            return result is not None
        except Exception as e:
            print(f"[ERROR] Erro ao definir canal de feedback: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_feedback_channel(self, guild_id: int) -> Optional[int]:
        """
        Retorna o ID do canal de feedback do servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            ID do canal de feedback ou None
        """
        config = await self.get_config(guild_id)
        
        if not config:
            return None
        
        return config.get('feedback_channel_id')
    
    async def set_deliveries_channel(self, guild_id: int, deliveries_channel_id: int) -> bool:
        """
        Define o canal de entregas/compras do servidor
        
        Args:
            guild_id: ID do servidor
            deliveries_channel_id: ID do canal de entregas
        
        Returns:
            True se salvou com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                deliveries_channel_id=deliveries_channel_id
            )
            return result is not None
        except Exception as e:
            print(f"[ERROR] Erro ao definir canal de entregas: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_deliveries_channel(self, guild_id: int) -> Optional[int]:
        """
        Retorna o ID do canal de entregas do servidor
        
        Args:
            guild_id: ID do servidor
        
        Returns:
            ID do canal de entregas ou None
        """
        config = await self.get_config(guild_id)
        
        if not config:
            return None
        
        return config.get('deliveries_channel_id')
    
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
            print(f"[ERROR] Erro ao desabilitar logs: {e}")
            return False
    
    # ===== MÉTODOS PARA SPLIT DE PAGAMENTO =====
    
    async def set_mercadopago_account(self, guild_id: int, account_id: str) -> bool:
        """
        Configura Account ID do Mercado Pago para split automático
        
        Args:
            guild_id: ID do servidor Discord
            account_id: Account ID do Mercado Pago
            
        Returns:
            True se configurado com sucesso
        """
        try:
            # Validar formato do Account ID
            if not self.validate_mercadopago_account(account_id):
                print(f"[ERROR] Account ID inválido: {account_id}")
                return False
            
            result = await self.create_or_update_config(
                guild_id=guild_id,
                mercadopago_account_id=account_id
            )
            
            if result:
                print(f"[OK] Account ID configurado para guild {guild_id}: {account_id}")
                return True
            else:
                print(f"[ERROR] Falha ao configurar Account ID para guild {guild_id}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Erro ao configurar Account ID: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_mercadopago_account(self, guild_id: int) -> Optional[str]:
        """
        Busca Account ID do Mercado Pago do servidor
        
        Args:
            guild_id: ID do servidor Discord
            
        Returns:
            Account ID ou None se não configurado
        """
        try:
            config = await self.get_config(guild_id)
            
            if not config:
                return None
            
            account_id = config.get('mercadopago_account_id')
            
            if account_id and self.validate_mercadopago_account(account_id):
                return account_id
            else:
                print(f"[WARNING] Account ID inválido para guild {guild_id}: {account_id}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Erro ao buscar Account ID: {e}")
            return None
    
    def validate_mercadopago_account(self, account_id: str) -> bool:
        """
        Valida formato do Account ID do Mercado Pago
        
        Args:
            account_id: Account ID para validar
            
        Returns:
            True se válido
        """
        if not account_id:
            return False
        
        # Remover espaços e caracteres especiais
        clean_id = str(account_id).strip()
        
        # Deve ser numérico
        if not clean_id.isdigit():
            print(f"[WARNING] Account ID deve ser numérico: {account_id}")
            return False
        
        # Deve ter entre 8-12 dígitos (formato típico do MP)
        if len(clean_id) < 8 or len(clean_id) > 12:
            print(f"[WARNING] Account ID deve ter 8-12 dígitos: {account_id} (len: {len(clean_id)})")
            return False
        
        # Não pode ser igual ao Account ID da plataforma
        platform_account_id = Config.MERCADOPAGO_ACCOUNT_ID if hasattr(Config, 'MERCADOPAGO_ACCOUNT_ID') else None
        if platform_account_id and clean_id == str(platform_account_id):
            print(f"[WARNING] Account ID não pode ser igual ao da plataforma: {account_id}")
            return False
        
        return True
    
    async def remove_mercadopago_account(self, guild_id: int) -> bool:
        """
        Remove configuração de Account ID (volta para modo centralizado)
        
        Args:
            guild_id: ID do servidor Discord
            
        Returns:
            True se removido com sucesso
        """
        try:
            result = await self.create_or_update_config(
                guild_id=guild_id,
                mercadopago_account_id=None
            )
            
            if result:
                print(f"[OK] Account ID removido para guild {guild_id}")
                return True
            else:
                print(f"[ERROR] Falha ao remover Account ID para guild {guild_id}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Erro ao remover Account ID: {e}")
            return False
    
    async def get_split_status(self, guild_id: int) -> Dict:
        """
        Retorna status da configuração de split
        
        Args:
            guild_id: ID do servidor Discord
            
        Returns:
            Dict com informações do split
        """
        try:
            config = await self.get_config(guild_id)
            
            if not config:
                return {
                    'configured': False,
                    'account_id': None,
                    'status': 'not_configured'
                }
            
            account_id = config.get('mercadopago_account_id')
            
            if not account_id:
                return {
                    'configured': False,
                    'account_id': None,
                    'status': 'not_configured'
                }
            
            is_valid = self.validate_mercadopago_account(account_id)
            
            return {
                'configured': is_valid,
                'account_id': account_id if is_valid else None,
                'status': 'configured' if is_valid else 'invalid',
                'masked_id': f"{account_id[:4]}****{account_id[-4:]}" if is_valid else account_id
            }
            
        except Exception as e:
            print(f"[ERROR] Erro ao buscar status do split: {e}")
            return {
                'configured': False,
                'account_id': None,
                'status': 'error'
            }

