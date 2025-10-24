#!/usr/bin/env python3
"""
Script de teste para verificar se a tabela guild_config e coluna ticket_allowed_products existem
Execute com: python test_guild_config.py
"""

import asyncio
from supabase import create_client
from config.config import Config

async def test_guild_config():
    """Testa a conexão e estrutura da tabela guild_config"""

    print("🔧 ========== TESTANDO GUILD CONFIG ==========")

    try:
        # Inicializar Supabase
        print(f"🔧 Conectando ao Supabase...")
        print(f"🔧 URL: {Config.SUPABASE_URL[:30]}...")
        print(f"🔧 Key: {Config.SUPABASE_KEY[:30]}...")

        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        print("✅ Supabase client criado")

        # Testar conexão com tabela guild_config
        print("🔧 Testando tabela guild_config...")
        result = supabase.table('guild_config').select('*').limit(1).execute()
        print(f"✅ Tabela guild_config existe! Result: {result}")

        # Verificar se a coluna ticket_allowed_products existe
        print("🔧 Verificando colunas da tabela guild_config...")

        # Query para verificar schema
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'guild_config'
        AND table_schema = 'public'
        ORDER BY column_name;
        """

        # Como não temos método direto, vamos tentar fazer uma query que use a coluna
        print("🔧 Testando se a coluna ticket_allowed_products existe...")

        try:
            # Tentar fazer uma query que use a coluna
            test_result = supabase.table('guild_config').select('guild_id, ticket_allowed_products').limit(1).execute()
            print(f"✅ Coluna ticket_allowed_products existe! Result: {test_result}")
        except Exception as e:
            print(f"❌ Coluna ticket_allowed_products NÃO existe! Erro: {e}")
            print("💡 Execute o arquivo database_ticket_product_filter.sql no Supabase")

        # Testar se podemos inserir/atualizar a coluna
        print("🔧 Testando insert/update com ticket_allowed_products...")

        try:
            test_guild_id = 123456789  # Guild ID de teste
            test_data = {
                'guild_id': test_guild_id,
                'guild_name': 'Test Guild',
                'ticket_allowed_products': [1, 2, 3]
            }

            result = supabase.table('guild_config').insert(test_data).execute()
            print(f"✅ Insert com ticket_allowed_products funcionou: {result}")

            # Limpar o teste
            supabase.table('guild_config').delete().eq('guild_id', test_guild_id).execute()
            print("✅ Teste limpo com sucesso")

        except Exception as e:
            print(f"❌ Erro no insert/update: {e}")
            print("💡 Verifique se a coluna ticket_allowed_products foi criada")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_guild_config())
