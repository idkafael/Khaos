import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações do bot"""
    
    # Token do Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', '')
    DISCORD_APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID', '')
    
    # Configurações do Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    
    # Configurações da API PushinPay
    PUSHINPAY_API_KEY = os.getenv('PUSHINPAY_API_KEY', '')
    PUSHINPAY_WEBHOOK_SECRET = os.getenv('PUSHINPAY_WEBHOOK_SECRET', '')
    PUSHINPAY_SANDBOX = os.getenv('PUSHINPAY_SANDBOX', 'false').lower() == 'true'
    WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', '')
    
    # Configurações do bot
    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
    BOT_OWNER_ID = int(os.getenv('BOT_OWNER_ID', '0'))
    
    # Configurações de pagamento
    PAYMENT_TIMEOUT_MINUTES = int(os.getenv('PAYMENT_TIMEOUT_MINUTES', '10'))
    PAYMENT_CHECK_INTERVAL_SECONDS = int(os.getenv('PAYMENT_CHECK_INTERVAL_SECONDS', '30'))
    
    # Configurações de log
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Configurações de banco de dados
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    @classmethod
    def validate_config(cls):
        """Valida se todas as configurações necessárias estão definidas"""
        required_configs = [
            ('DISCORD_TOKEN', cls.DISCORD_TOKEN),
            ('SUPABASE_URL', cls.SUPABASE_URL),
            ('SUPABASE_KEY', cls.SUPABASE_KEY),
            ('PUSHINPAY_API_KEY', cls.PUSHINPAY_API_KEY)
        ]
        
        missing_configs = []
        for config_name, config_value in required_configs:
            if not config_value:
                missing_configs.append(config_name)
        
        if missing_configs:
            raise ValueError(f"Configurações obrigatórias ausentes: {', '.join(missing_configs)}")
        
        return True
    
    @classmethod
    def get_database_url(cls):
        """Retorna a URL de conexão com o banco de dados"""
        return f"postgresql://{cls.SUPABASE_URL.split('//')[1]}"
    
    @classmethod
    def is_production(cls):
        """Verifica se está em ambiente de produção"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    @classmethod
    def get_log_config(cls):
        """Retorna configuração de logging"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'default': {
                    'level': cls.LOG_LEVEL,
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
                'file': {
                    'level': cls.LOG_LEVEL,
                    'formatter': 'standard',
                    'class': 'logging.FileHandler',
                    'filename': cls.LOG_FILE,
                    'mode': 'a',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['default', 'file'],
                    'level': cls.LOG_LEVEL,
                    'propagate': False
                }
            }
        }
