#!/usr/bin/env python3
"""
Script para criar o arquivo .env automaticamente
"""

def create_env_file():
    """Cria o arquivo .env com todas as credenciais"""
    
    env_content = """# Configurações do Bot Discord ✅
DISCORD_TOKEN=842c8e29352ebd03e85b29f8c1c4ed6ee2e981194ad0236c153e3bb234c3848f
DISCORD_APPLICATION_ID=784058182515425310

# Configurações do Supabase ✅
SUPABASE_URL=https://sxsaxcqliuiolktypwkf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4c2F4Y3FsaXVpb2xrdHlwd2tmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NTQwNDksImV4cCI6MjA3NjQzMDA0OX0.Qc-DINC-FC9oPbI4BBpxbtF9OmTMUN8ecC1gDSTatbY

# Configurações da API PushinPay ✅
PUSHINPAY_API_KEY=50790|dakuggRtFoHjIZb2XpYYbDoa2exlT5NPspJayboI40bfb10f
PUSHINPAY_WEBHOOK_SECRET=seu_webhook_secret_aqui
PUSHINPAY_SANDBOX=true
WEBHOOK_BASE_URL=https://seu-dominio.com

# Configurações opcionais
BOT_PREFIX=!
BOT_OWNER_ID=123456789
PAYMENT_TIMEOUT_MINUTES=10
PAYMENT_CHECK_INTERVAL_SECONDS=30
LOG_LEVEL=INFO
LOG_FILE=bot.log
ENVIRONMENT=development
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso!")
        print("📁 Localização: .env (na raiz do projeto)")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        print("💡 Copie manualmente o conteúdo de 'configuracao_completa.env' para '.env'")
        return False

def show_manual_instructions():
    """Mostra instruções manuais"""
    print("\n" + "="*60)
    print("📝 INSTRUÇÕES MANUAIS")
    print("="*60)
    
    print("\n1. Crie um arquivo chamado '.env' na raiz do projeto")
    print("2. Copie o conteúdo do arquivo 'configuracao_completa.env'")
    print("3. Cole no arquivo '.env'")
    print("4. Salve o arquivo")
    
    print("\n📋 Conteúdo para copiar:")
    print("-" * 40)
    
    with open('configuracao_completa.env', 'r', encoding='utf-8') as f:
        print(f.read())
    
    print("-" * 40)

def main():
    """Função principal"""
    print("🔧 CRIADOR DE ARQUIVO .ENV")
    print("="*40)
    
    # Tentar criar automaticamente
    if create_env_file():
        print("\n🎉 Arquivo .env criado automaticamente!")
        print("✅ Todas as suas credenciais estão configuradas")
        print("\n📋 Próximos passos:")
        print("1. Execute o SQL no Supabase")
        print("2. Faça deploy do bot")
        print("3. Convide o bot para seu servidor")
    else:
        show_manual_instructions()

if __name__ == "__main__":
    main()
