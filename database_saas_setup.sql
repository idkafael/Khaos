-- =============================================
-- SETUP MICRO SAAS - SISTEMA DE CARTEIRA VIRTUAL
-- =============================================
-- Execute este SQL no Supabase SQL Editor
-- Cria estrutura para gerenciar pagamentos centralizados,
-- carteira virtual dos servidores e saques automáticos

-- =============================================
-- 1. TABELA DE CARTEIRAS (Saldo de cada servidor)
-- =============================================

CREATE TABLE IF NOT EXISTS guild_wallets (
    guild_id BIGINT PRIMARY KEY,
    balance_available DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (balance_available >= 0),
    balance_pending DECIMAL(10,2) DEFAULT 0.00 NOT NULL CHECK (balance_pending >= 0),
    total_earned DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    total_withdrawn DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    platform_fees_paid DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    pix_key VARCHAR(255),
    pix_type VARCHAR(20) CHECK (pix_type IN ('cpf', 'cnpj', 'email', 'phone', 'random')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE guild_wallets IS 'Carteira virtual de cada servidor Discord';
COMMENT ON COLUMN guild_wallets.balance_available IS 'Saldo disponível para saque';
COMMENT ON COLUMN guild_wallets.balance_pending IS 'Saldo pendente (aguardando confirmação)';
COMMENT ON COLUMN guild_wallets.total_earned IS 'Total ganho histórico';
COMMENT ON COLUMN guild_wallets.total_withdrawn IS 'Total sacado histórico';
COMMENT ON COLUMN guild_wallets.platform_fees_paid IS 'Total de taxas pagas à plataforma';
COMMENT ON COLUMN guild_wallets.pix_key IS 'Chave Pix padrão do servidor';

-- =============================================
-- 2. TABELA DE TRANSAÇÕES DA CARTEIRA
-- =============================================

CREATE TABLE IF NOT EXISTS wallet_transactions (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL REFERENCES guild_wallets(guild_id) ON DELETE CASCADE,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('credit_sale', 'debit_withdrawal', 'fee_sale', 'fee_withdrawal', 'refund', 'adjustment')),
    gross_amount DECIMAL(10,2) NOT NULL,
    platform_fee DECIMAL(10,2) DEFAULT 0.00,
    net_amount DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE wallet_transactions IS 'Histórico de todas movimentações financeiras da carteira';
COMMENT ON COLUMN wallet_transactions.type IS 'Tipo: credit_sale (venda), debit_withdrawal (saque), fee_sale (taxa venda), fee_withdrawal (taxa saque)';
COMMENT ON COLUMN wallet_transactions.gross_amount IS 'Valor bruto da transação';
COMMENT ON COLUMN wallet_transactions.platform_fee IS 'Taxa cobrada pela plataforma';
COMMENT ON COLUMN wallet_transactions.net_amount IS 'Valor líquido (após taxas)';
COMMENT ON COLUMN wallet_transactions.balance_after IS 'Saldo da carteira após esta transação';

CREATE INDEX idx_wallet_transactions_guild_id ON wallet_transactions(guild_id);
CREATE INDEX idx_wallet_transactions_type ON wallet_transactions(type);
CREATE INDEX idx_wallet_transactions_created_at ON wallet_transactions(created_at DESC);

-- =============================================
-- 3. TABELA DE SOLICITAÇÕES DE SAQUE
-- =============================================

CREATE TABLE IF NOT EXISTS withdrawal_requests (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL REFERENCES guild_wallets(guild_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    amount_requested DECIMAL(10,2) NOT NULL CHECK (amount_requested > 0),
    fee_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    net_amount DECIMAL(10,2) NOT NULL,
    pix_key VARCHAR(255) NOT NULL,
    pix_type VARCHAR(20) NOT NULL CHECK (pix_type IN ('cpf', 'cnpj', 'email', 'phone', 'random')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'rejected', 'cancelled')),
    gateway_transaction_id VARCHAR(255),
    error_message TEXT,
    requested_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    completed_at TIMESTAMP
);

COMMENT ON TABLE withdrawal_requests IS 'Solicitações de saque dos servidores';
COMMENT ON COLUMN withdrawal_requests.amount_requested IS 'Valor solicitado pelo usuário';
COMMENT ON COLUMN withdrawal_requests.fee_amount IS 'Taxa de saque (3%)';
COMMENT ON COLUMN withdrawal_requests.net_amount IS 'Valor que o usuário receberá';
COMMENT ON COLUMN withdrawal_requests.gateway_transaction_id IS 'ID da transação no gateway (Mercado Pago)';

CREATE INDEX idx_withdrawal_requests_guild_id ON withdrawal_requests(guild_id);
CREATE INDEX idx_withdrawal_requests_status ON withdrawal_requests(status);
CREATE INDEX idx_withdrawal_requests_requested_at ON withdrawal_requests(requested_at DESC);

-- =============================================
-- 4. TABELA DE TAXAS DA PLATAFORMA
-- =============================================

CREATE TABLE IF NOT EXISTS platform_fees (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL REFERENCES guild_wallets(guild_id) ON DELETE CASCADE,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    withdrawal_id INTEGER REFERENCES withdrawal_requests(id) ON DELETE SET NULL,
    fee_type VARCHAR(20) NOT NULL CHECK (fee_type IN ('sale_fixed', 'withdrawal_percent')),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE platform_fees IS 'Registro de todas as comissões cobradas pela plataforma';
COMMENT ON COLUMN platform_fees.fee_type IS 'sale_fixed = R$ 0,80 por venda | withdrawal_percent = 3% do saque';

CREATE INDEX idx_platform_fees_guild_id ON platform_fees(guild_id);
CREATE INDEX idx_platform_fees_created_at ON platform_fees(created_at DESC);

-- =============================================
-- 5. ADICIONAR CAMPO GATEWAY EM TRANSACTIONS
-- =============================================

ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS gateway_used VARCHAR(20) CHECK (gateway_used IN ('mercadopago', 'pushinpay', 'asaas', 'stripe'));

ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS platform_fee DECIMAL(10,2) DEFAULT 0.00;

COMMENT ON COLUMN transactions.gateway_used IS 'Gateway utilizado para processar o pagamento';
COMMENT ON COLUMN transactions.platform_fee IS 'Taxa da plataforma cobrada (R$ 0,80 fixo)';

-- =============================================
-- 6. TABELA DE LOGS DE AUDITORIA
-- =============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Logs de auditoria de todas operações financeiras';
COMMENT ON COLUMN audit_logs.action IS 'Ação realizada (credit_wallet, debit_wallet, request_withdrawal, etc)';

CREATE INDEX idx_audit_logs_guild_id ON audit_logs(guild_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- =============================================
-- 7. FUNÇÃO: Atualizar updated_at automaticamente
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_guild_wallets_updated_at
    BEFORE UPDATE ON guild_wallets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 8. FUNÇÃO: Creditar carteira (após venda)
-- =============================================

CREATE OR REPLACE FUNCTION credit_wallet_from_sale(
    p_guild_id BIGINT,
    p_transaction_id INTEGER,
    p_gross_amount DECIMAL(10,2),
    p_platform_fee DECIMAL(10,2) DEFAULT 0.80
)
RETURNS VOID AS $$
DECLARE
    v_net_amount DECIMAL(10,2);
    v_new_balance DECIMAL(10,2);
BEGIN
    -- Calcular valor líquido (valor bruto - taxa de R$ 0,80)
    v_net_amount := p_gross_amount - p_platform_fee;
    
    -- Inserir ou criar carteira se não existir
    INSERT INTO guild_wallets (guild_id, balance_available, total_earned, platform_fees_paid)
    VALUES (p_guild_id, v_net_amount, v_net_amount, p_platform_fee)
    ON CONFLICT (guild_id) 
    DO UPDATE SET
        balance_available = guild_wallets.balance_available + v_net_amount,
        total_earned = guild_wallets.total_earned + v_net_amount,
        platform_fees_paid = guild_wallets.platform_fees_paid + p_platform_fee,
        updated_at = NOW()
    RETURNING balance_available INTO v_new_balance;
    
    -- Registrar movimentação de crédito
    INSERT INTO wallet_transactions (
        guild_id, transaction_id, type, gross_amount, platform_fee, net_amount, balance_after, description
    ) VALUES (
        p_guild_id, p_transaction_id, 'credit_sale', p_gross_amount, p_platform_fee, v_net_amount, v_new_balance,
        'Crédito de venda - Taxa plataforma: R$ ' || p_platform_fee
    );
    
    -- Registrar taxa da plataforma
    INSERT INTO platform_fees (guild_id, transaction_id, fee_type, amount, description)
    VALUES (p_guild_id, p_transaction_id, 'sale_fixed', p_platform_fee, 'Taxa fixa por venda');
    
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION credit_wallet_from_sale IS 'Credita carteira do servidor após venda (desconta R$ 0,80)';

-- =============================================
-- 9. FUNÇÃO: Debitar carteira (saque)
-- =============================================

CREATE OR REPLACE FUNCTION debit_wallet_from_withdrawal(
    p_guild_id BIGINT,
    p_withdrawal_id INTEGER,
    p_amount DECIMAL(10,2),
    p_fee_percent DECIMAL(5,2) DEFAULT 3.00
)
RETURNS BOOLEAN AS $$
DECLARE
    v_fee_amount DECIMAL(10,2);
    v_total_debit DECIMAL(10,2);
    v_current_balance DECIMAL(10,2);
    v_new_balance DECIMAL(10,2);
BEGIN
    -- Calcular taxa de saque (3%)
    v_fee_amount := ROUND(p_amount * (p_fee_percent / 100), 2);
    v_total_debit := p_amount + v_fee_amount;
    
    -- Verificar saldo disponível
    SELECT balance_available INTO v_current_balance
    FROM guild_wallets
    WHERE guild_id = p_guild_id;
    
    IF v_current_balance IS NULL OR v_current_balance < p_amount THEN
        RETURN FALSE; -- Saldo insuficiente
    END IF;
    
    -- Debitar da carteira
    UPDATE guild_wallets
    SET balance_available = balance_available - p_amount,
        total_withdrawn = total_withdrawn + p_amount,
        platform_fees_paid = platform_fees_paid + v_fee_amount,
        updated_at = NOW()
    WHERE guild_id = p_guild_id
    RETURNING balance_available INTO v_new_balance;
    
    -- Registrar movimentação de débito
    INSERT INTO wallet_transactions (
        guild_id, type, gross_amount, platform_fee, net_amount, balance_after, description
    ) VALUES (
        p_guild_id, 'debit_withdrawal', p_amount, v_fee_amount, p_amount - v_fee_amount, v_new_balance,
        'Saque processado - Taxa: ' || p_fee_percent || '%'
    );
    
    -- Registrar taxa de saque
    INSERT INTO platform_fees (guild_id, withdrawal_id, fee_type, amount, description)
    VALUES (p_guild_id, p_withdrawal_id, 'withdrawal_percent', v_fee_amount, 'Taxa de saque: ' || p_fee_percent || '%');
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION debit_wallet_from_withdrawal IS 'Debita carteira do servidor para saque (cobra 3%)';

-- =============================================
-- 10. ADICIONAR CAMPO preferred_gateway EM guild_config
-- =============================================

ALTER TABLE guild_config 
ADD COLUMN IF NOT EXISTS preferred_gateway VARCHAR(20) DEFAULT 'mercadopago' 
CHECK (preferred_gateway IN ('mercadopago', 'pushinpay', 'asaas', 'stripe'));

COMMENT ON COLUMN guild_config.preferred_gateway IS 'Gateway preferido do servidor (padrão: mercadopago)';

-- =============================================
-- 11. DESABILITAR RLS (Row Level Security)
-- =============================================

ALTER TABLE guild_wallets DISABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawal_requests DISABLE ROW LEVEL SECURITY;
ALTER TABLE platform_fees DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

-- =============================================
-- 12. GRANTS (Permissões)
-- =============================================

-- Garantir que o service role tenha acesso total
-- (Supabase configura automaticamente, mas explicitamos aqui)

-- =============================================
-- ✅ SETUP COMPLETO!
-- =============================================

-- Verificação: Ver todas as tabelas criadas
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN ('guild_wallets', 'wallet_transactions', 'withdrawal_requests', 'platform_fees', 'audit_logs')
ORDER BY table_name;

