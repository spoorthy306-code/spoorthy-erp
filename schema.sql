-- SPOORTHY QUANTUM OS — PostgreSQL Schema
-- Full DDL with indexes, RLS, JSONB for quantum results, partitioning

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Entities
CREATE TABLE entities (
    entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    gstin VARCHAR(15) UNIQUE,
    pan VARCHAR(10) UNIQUE,
    tan VARCHAR(10),
    address JSONB,
    currency VARCHAR(3) DEFAULT 'INR',
    reporting_currency VARCHAR(3) DEFAULT 'INR',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chart of Accounts
CREATE TABLE chart_of_accounts (
    account_code VARCHAR(20) PRIMARY KEY,
    entity_id UUID REFERENCES entities(entity_id),
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50), -- Asset, Liability, Equity, Revenue, Expense
    parent_code VARCHAR(20),
    level INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal Entries (Partitioned by period)
CREATE TABLE journal_entries (
    entry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    entry_date DATE NOT NULL,
    period VARCHAR(7), -- YYYY-MM
    narration TEXT,
    total_debit DECIMAL(15,2) DEFAULT 0,
    total_credit DECIMAL(15,2) DEFAULT 0,
    posted_by VARCHAR(100),
    pqc_signature TEXT,
    quantum_job_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (period);

-- Journal Lines
CREATE TABLE journal_lines (
    line_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entry_id UUID REFERENCES journal_entries(entry_id),
    account_code VARCHAR(20) REFERENCES chart_of_accounts(account_code),
    debit DECIMAL(15,2) DEFAULT 0,
    credit DECIMAL(15,2) DEFAULT 0,
    description TEXT
);

-- Bank Transactions
CREATE TABLE bank_transactions (
    txn_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    bank_account VARCHAR(50),
    txn_date DATE,
    description TEXT,
    amount DECIMAL(15,2),
    balance DECIMAL(15,2),
    reconciled BOOLEAN DEFAULT FALSE,
    reconciled_entry_id UUID REFERENCES journal_entries(entry_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoices
CREATE TABLE invoices (
    invoice_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    invoice_no VARCHAR(50) UNIQUE,
    invoice_date DATE,
    buyer_gstin VARCHAR(15),
    buyer_name VARCHAR(255),
    total_amount DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    irn TEXT,
    qr_code TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fixed Assets
CREATE TABLE fixed_assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    asset_code VARCHAR(50) UNIQUE,
    description TEXT,
    cost DECIMAL(15,2),
    accumulated_depreciation DECIMAL(15,2) DEFAULT 0,
    nbv DECIMAL(15,2),
    depreciation_method VARCHAR(10), -- SLM, WDV
    useful_life_years INT,
    residual_value DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory
CREATE TABLE inventory (
    sku VARCHAR(50) PRIMARY KEY,
    entity_id UUID REFERENCES entities(entity_id),
    description TEXT,
    qty_on_hand DECIMAL(10,2),
    unit_cost DECIMAL(10,2),
    total_value DECIMAL(15,2),
    costing_method VARCHAR(20) DEFAULT 'FIFO',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employees
CREATE TABLE employees (
    employee_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    name VARCHAR(255),
    pan VARCHAR(10),
    uan VARCHAR(12),
    basic_salary DECIMAL(12,2),
    hra DECIMAL(12,2),
    lta DECIMAL(12,2),
    medical DECIMAL(12,2),
    nps DECIMAL(12,2),
    pf_employee DECIMAL(12,2),
    joined_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- Payroll Runs
CREATE TABLE payroll_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    period VARCHAR(7),
    total_gross DECIMAL(15,2),
    total_deductions DECIMAL(15,2),
    total_net DECIMAL(15,2),
    pf_employer DECIMAL(15,2),
    esic_employer DECIMAL(15,2),
    pt DECIMAL(15,2),
    tds DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loans
CREATE TABLE loans (
    loan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    facility_type VARCHAR(50),
    bank VARCHAR(100),
    sanctioned_amount DECIMAL(15,2),
    outstanding DECIMAL(15,2),
    rate_pct DECIMAL(5,2),
    emi DECIMAL(12,2),
    tenure_months INT,
    disbursement_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- Portfolios
CREATE TABLE portfolios (
    portfolio_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    name VARCHAR(255),
    total_value DECIMAL(15,2),
    holdings JSONB, -- [{"ticker": "NIFTY", "qty": 100, "price": 18500}]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    user_id VARCHAR(100),
    action VARCHAR(100),
    table_name VARCHAR(50),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Quantum Jobs
CREATE TABLE quantum_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    module VARCHAR(50),
    solver VARCHAR(50),
    qubo_size INT,
    energy DECIMAL(10,4),
    solve_time_ms INT,
    result JSONB,
    status VARCHAR(20) DEFAULT 'COMPLETED',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GST Returns
CREATE TABLE gst_returns (
    return_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(entity_id),
    return_type VARCHAR(10), -- GSTR1, GSTR3B
    period VARCHAR(7),
    json_payload JSONB,
    status VARCHAR(20) DEFAULT 'FILED',
    arn VARCHAR(50),
    filed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_journal_entries_entity_period ON journal_entries(entity_id, period);
CREATE INDEX idx_journal_entries_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_lines_entry ON journal_lines(entry_id);
CREATE INDEX idx_journal_lines_account ON journal_lines(account_code);
CREATE INDEX idx_bank_txns_entity_date ON bank_transactions(entity_id, txn_date);
CREATE INDEX idx_invoices_entity_date ON invoices(entity_id, invoice_date);
CREATE INDEX idx_fixed_assets_entity ON fixed_assets(entity_id);
CREATE INDEX idx_inventory_entity ON inventory(entity_id);
CREATE INDEX idx_employees_entity ON employees(entity_id);
CREATE INDEX idx_payroll_runs_entity_period ON payroll_runs(entity_id, period);
CREATE INDEX idx_loans_entity ON loans(entity_id);
CREATE INDEX idx_portfolios_entity ON portfolios(entity_id);
CREATE INDEX idx_audit_log_entity_timestamp ON audit_log(entity_id, timestamp);
CREATE INDEX idx_quantum_jobs_entity_module ON quantum_jobs(entity_id, module);
CREATE INDEX idx_gst_returns_entity_period ON gst_returns(entity_id, period);

-- Row Level Security
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
-- Add policies as needed for multi-tenant

-- Partitioning for journal_entries
CREATE TABLE journal_entries_2025_04 PARTITION OF journal_entries FOR VALUES FROM ('2025-04') TO ('2025-05');
CREATE TABLE journal_entries_2025_05 PARTITION OF journal_entries FOR VALUES FROM ('2025-05') TO ('2025-06');
-- Add more partitions as needed

-- Views
CREATE VIEW trial_balance AS
SELECT
    entity_id,
    account_code,
    SUM(debit) AS total_debit,
    SUM(credit) AS total_credit,
    SUM(debit - credit) AS balance
FROM journal_lines jl
JOIN journal_entries je ON jl.entry_id = je.entry_id
GROUP BY entity_id, account_code;

CREATE VIEW pnl_statement AS
SELECT
    entity_id,
    period,
    SUM(CASE WHEN coa.account_type = 'Revenue' THEN jl.credit - jl.debit ELSE 0 END) AS revenue,
    SUM(CASE WHEN coa.account_type = 'Expense' THEN jl.debit - jl.credit ELSE 0 END) AS expenses,
    SUM(CASE WHEN coa.account_type = 'Revenue' THEN jl.credit - jl.debit ELSE 0 END) -
    SUM(CASE WHEN coa.account_type = 'Expense' THEN jl.debit - jl.credit ELSE 0 END) AS pbt
FROM journal_lines jl
JOIN journal_entries je ON jl.entry_id = je.entry_id
JOIN chart_of_accounts coa ON jl.account_code = coa.account_code
GROUP BY entity_id, period;