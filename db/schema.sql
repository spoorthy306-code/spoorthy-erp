-- ============================================================
-- SPOORTHY ERP - COMPLETE DATABASE SCHEMA
-- PostgreSQL 14+
-- ============================================================

CREATE TABLE IF NOT EXISTS entities (
    entity_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gstin VARCHAR(15) UNIQUE,
    pan VARCHAR(10) UNIQUE,
    tan VARCHAR(10) UNIQUE,
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',
    currency VARCHAR(3) DEFAULT 'INR',
    fiscal_year_start DATE,
    fiscal_year_end DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chart_of_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    account_subtype VARCHAR(50),
    opening_balance NUMERIC(15, 2) DEFAULT 0,
    balance_type VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_coa_entity ON chart_of_accounts(entity_id);

CREATE TABLE IF NOT EXISTS journal_entries (
    entry_id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    description TEXT,
    reference_number VARCHAR(255),
    period VARCHAR(7) NOT NULL,
    total_debit NUMERIC(15, 2) NOT NULL DEFAULT 0,
    total_credit NUMERIC(15, 2) NOT NULL DEFAULT 0,
    is_posted BOOLEAN DEFAULT FALSE,
    posted_by VARCHAR(100),
    posted_date TIMESTAMP,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_je_entity_period ON journal_entries(entity_id, period);
CREATE INDEX IF NOT EXISTS idx_je_date ON journal_entries(entry_date);

CREATE TABLE IF NOT EXISTS journal_lines (
    line_id SERIAL PRIMARY KEY,
    entry_id INTEGER REFERENCES journal_entries(entry_id) ON DELETE CASCADE,
    account_id VARCHAR(50) REFERENCES chart_of_accounts(account_id),
    debit_amount NUMERIC(15, 2) DEFAULT 0,
    credit_amount NUMERIC(15, 2) DEFAULT 0,
    nature VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_jl_entry ON journal_lines(entry_id);

CREATE TABLE IF NOT EXISTS ledgers (
    id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id),
    nature VARCHAR(50) NOT NULL,
    account_id VARCHAR(50) REFERENCES chart_of_accounts(account_id),
    period VARCHAR(7),
    debit_amount NUMERIC(15, 2) DEFAULT 0,
    credit_amount NUMERIC(15, 2) DEFAULT 0,
    reference_number VARCHAR(255),
    description TEXT,
    posting_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_module VARCHAR(100),
    is_reversed BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ledgers_entity ON ledgers(entity_id);
CREATE INDEX IF NOT EXISTS idx_ledgers_period ON ledgers(period);
CREATE INDEX IF NOT EXISTS idx_ledgers_nature ON ledgers(nature);
CREATE INDEX IF NOT EXISTS idx_ledgers_account ON ledgers(account_id);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    due_date DATE,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_gstin VARCHAR(15),
    total_amount NUMERIC(15, 2),
    tax_amount NUMERIC(15, 2),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_invoices_entity ON invoices(entity_id);

CREATE TABLE IF NOT EXISTS fixed_assets (
    asset_id VARCHAR(50) PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id),
    description VARCHAR(255),
    asset_cost NUMERIC(15, 2),
    date_of_purchase DATE,
    useful_life_years INTEGER,
    depreciation_method VARCHAR(50),
    accumulated_depreciation NUMERIC(15, 2) DEFAULT 0,
    net_book_value NUMERIC(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    sku VARCHAR(50) PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id),
    item_name VARCHAR(255),
    unit_cost NUMERIC(15, 2),
    quantity_on_hand INTEGER DEFAULT 0,
    valuation_method VARCHAR(50),
    closing_value NUMERIC(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gst_returns (
    return_id VARCHAR(50) PRIMARY KEY,
    entity_id VARCHAR(50) REFERENCES entities(entity_id),
    return_type VARCHAR(50),
    period VARCHAR(7),
    status VARCHAR(20),
    filing_date TIMESTAMP,
    arn VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    entity_id VARCHAR(50),
    user_id VARCHAR(100),
    action VARCHAR(255),
    module VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);
CREATE INDEX IF NOT EXISTS idx_audit_entity_date ON audit_log(entity_id, timestamp);

CREATE TABLE IF NOT EXISTS quantum_jobs (
    job_id VARCHAR(100) PRIMARY KEY,
    entity_id VARCHAR(50),
    job_type VARCHAR(100),
    status VARCHAR(20),
    qubo_energy NUMERIC(15, 6),
    solve_time_ms INTEGER,
    result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
