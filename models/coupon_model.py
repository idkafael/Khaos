from config.config import Config
from supabase import create_client
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class CouponModel:
    def __init__(self):
        """Inicializa o modelo de cupons"""
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    async def get_coupon_by_code(self, code: str, guild_id: int) -> Optional[Dict]:
        """Busca um cupom pelo código em um servidor específico
        
        Args:
            code: Código do cupom (case-insensitive)
            guild_id: ID do servidor Discord
            
        Returns:
            Dados do cupom ou None se não encontrado
        """
        try:
            code = code.upper().strip()
            response = self.supabase.table('coupons')\
                .select('*')\
                .eq('code', code)\
                .eq('guild_id', guild_id)\
                .eq('active', True)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Erro ao buscar cupom: {e}")
            return None
    
    async def validate_coupon(self, code: str, user_id: int, amount: float, guild_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """Valida um cupom e retorna se é válido + mensagem + dados
        
        Args:
            code: Código do cupom
            user_id: ID do usuário
            amount: Valor da compra
            guild_id: ID do servidor Discord
            
        Returns:
            (válido: bool, mensagem: str, dados_cupom: dict ou None)
        """
        try:
            # Buscar cupom
            coupon = await self.get_coupon_by_code(code, guild_id)
            
            if not coupon:
                return False, "Cupom não encontrado ou inativo.", None
            
            # Verificar expiração
            if coupon.get('expires_at'):
                expires_at = datetime.fromisoformat(coupon['expires_at'].replace('Z', '+00:00'))
                if datetime.now(expires_at.tzinfo) > expires_at:
                    return False, "Cupom expirado.", None
            
            # Verificar limite de usos totais
            if coupon.get('max_uses') is not None:
                if coupon.get('uses_count', 0) >= coupon['max_uses']:
                    return False, "Cupom atingiu o limite de usos.", None
            
            # Verificar se é um uso por usuário
            if coupon.get('one_per_user', False):
                # Verificar se usuário já usou este cupom
                usage_response = self.supabase.table('coupon_usage')\
                    .select('id')\
                    .eq('coupon_id', coupon['id'])\
                    .eq('user_id', user_id)\
                    .execute()
                
                if usage_response.data and len(usage_response.data) > 0:
                    return False, "Você já usou este cupom anteriormente.", None
            
            # Calcular desconto
            discount_percent = float(coupon['discount_percent'])
            discount_amount = amount * (discount_percent / 100)
            final_amount = amount - discount_amount
            
            # Adicionar informações calculadas ao cupom
            coupon['calculated_discount'] = discount_amount
            coupon['calculated_final_amount'] = final_amount
            
            return True, f"Cupom válido! Desconto de {discount_percent}%", coupon
            
        except Exception as e:
            print(f"Erro ao validar cupom: {e}")
            import traceback
            traceback.print_exc()
            return False, "Erro ao validar cupom.", None
    
    async def use_coupon(self, coupon_id: int, user_id: int, transaction_id: int, discount_amount: float) -> bool:
        """Registra o uso de um cupom
        
        Args:
            coupon_id: ID do cupom
            user_id: ID do usuário
            transaction_id: ID da transação
            discount_amount: Valor do desconto aplicado
            
        Returns:
            True se registrado com sucesso
        """
        try:
            # Registrar uso na tabela coupon_usage
            usage_data = {
                'coupon_id': coupon_id,
                'user_id': user_id,
                'transaction_id': transaction_id,
                'discount_amount': discount_amount
            }
            
            self.supabase.table('coupon_usage').insert(usage_data).execute()
            
            # Incrementar contador de usos
            self.supabase.rpc('increment_coupon_uses', {'coupon_id': coupon_id}).execute()
            
            return True
            
        except Exception as e:
            print(f"Erro ao registrar uso do cupom: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def create_coupon(self, data: Dict) -> Tuple[bool, str]:
        """Cria um novo cupom
        
        Args:
            data: Dados do cupom (code, discount_percent, etc)
            
        Returns:
            (sucesso: bool, mensagem: str)
        """
        try:
            # Normalizar código
            data['code'] = data['code'].upper().strip()
            
            # Verificar se código já existe
            existing = await self.get_coupon_by_code(data['code'])
            if existing:
                return False, "Já existe um cupom com este código."
            
            # Inserir cupom
            self.supabase.table('coupons').insert(data).execute()
            
            return True, f"Cupom {data['code']} criado com sucesso!"
            
        except Exception as e:
            print(f"Erro ao criar cupom: {e}")
            import traceback
            traceback.print_exc()
            return False, "Erro ao criar cupom."
    
    async def update_coupon(self, coupon_id: int, data: Dict) -> Tuple[bool, str]:
        """Atualiza um cupom existente
        
        Args:
            coupon_id: ID do cupom
            data: Dados a atualizar
            
        Returns:
            (sucesso: bool, mensagem: str)
        """
        try:
            data['updated_at'] = datetime.now().isoformat()
            
            self.supabase.table('coupons').update(data).eq('id', coupon_id).execute()
            
            return True, "Cupom atualizado com sucesso!"
            
        except Exception as e:
            print(f"Erro ao atualizar cupom: {e}")
            return False, "Erro ao atualizar cupom."
    
    async def delete_coupon(self, code: str) -> Tuple[bool, str]:
        """Desativa um cupom (não deleta do banco)
        
        Args:
            code: Código do cupom
            
        Returns:
            (sucesso: bool, mensagem: str)
        """
        try:
            code = code.upper().strip()
            
            self.supabase.table('coupons').update({'active': False}).eq('code', code).execute()
            
            return True, f"Cupom {code} desativado com sucesso!"
            
        except Exception as e:
            print(f"Erro ao deletar cupom: {e}")
            return False, "Erro ao deletar cupom."
    
    async def get_all_coupons(self, active_only: bool = True) -> List[Dict]:
        """Lista todos os cupons
        
        Args:
            active_only: Se True, retorna apenas cupons ativos
            
        Returns:
            Lista de cupons
        """
        try:
            query = self.supabase.table('coupons').select('*')
            
            if active_only:
                query = query.eq('active', True)
            
            response = query.order('created_at', desc=True).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Erro ao listar cupons: {e}")
            return []
    
    async def get_coupon_stats(self, code: str) -> Optional[Dict]:
        """Retorna estatísticas de uso de um cupom
        
        Args:
            code: Código do cupom
            
        Returns:
            Estatísticas do cupom ou None
        """
        try:
            code = code.upper().strip()
            
            # Buscar cupom
            coupon = await self.get_coupon_by_code(code)
            if not coupon:
                return None
            
            # Buscar usos
            usage_response = self.supabase.table('coupon_usage')\
                .select('*')\
                .eq('coupon_id', coupon['id'])\
                .order('used_at', desc=True)\
                .execute()
            
            usages = usage_response.data if usage_response.data else []
            
            # Calcular estatísticas
            total_uses = len(usages)
            total_discount = sum(float(u.get('discount_amount', 0)) for u in usages)
            
            # Pegar últimos usuários (IDs únicos)
            recent_users = []
            seen_users = set()
            for usage in usages:
                user_id = usage.get('user_id')
                if user_id and user_id not in seen_users:
                    recent_users.append(user_id)
                    seen_users.add(user_id)
                if len(recent_users) >= 10:
                    break
            
            stats = {
                'coupon': coupon,
                'total_uses': total_uses,
                'total_discount': total_discount,
                'recent_users': recent_users,
                'usages': usages[:10]  # Últimos 10 usos
            }
            
            return stats
            
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            import traceback
            traceback.print_exc()
            return None

