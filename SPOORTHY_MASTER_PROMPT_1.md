# SPOORTHY QUANTUM OS — MASTER BUILD PROMPT
## End-to-End: Backend · Data Layer · Frontend · Logs · Scripts · Missing Completions
### Version: 1.0 | Generated: April 2026

---

## CONTEXT & CODEBASE SUMMARY

You have `spoorthy_finance_complete.py` — a **~11,163-line Python monolith** implementing **Spoorthy Quantum OS**, a quantum-accelerated accounting and financial services platform for Indian enterprises.

### Existing Modules (25 implemented):

**Quantum Accounting (M-A1 to M-A12 + extensions):**
- A1 Quantum Reconciliation Engine (D-Wave QUBO many-to-many matching)
- A2 Real-Time Financial Consolidation (multi-entity, multi-currency, IFRS 10)
- A3 Quantum Audit Trail & Immutable Ledger (PQC ML-DSA signed, hash-chained)
- A4 Transfer Pricing Engine (OECD BEPS, TNMM+QUBO, CbCR)
- A5 Working Capital Optimizer (AP/AR/Inventory QUBO)
- A6 Financial Statement Generator (Ind AS / IFRS / US GAAP — P&L, BS, CF, SCE)
- A7 Intercompany Elimination Engine
- A8 Quantum Payroll Structure Optimizer (India HRA/LTA/NPS)
- A9 Continuous Accounting Engine (perpetual real-time close)
- A10 Quantum Bad Debt Provisioning (IFRS 9 ECL)
- A11 Quantum Collections Optimizer
- A12 Quantum Accounts Payable Optimizer
- Cost Centre Module, Standard Costing, Job Costing, Process Costing
- Master Invoice Engine (e-Invoice IRN+QR, GST doc types)
- Intercompany Ledger, Project Ledger (EVM), Currency Ledger, Loan Ledger, Provision Ledger
- GSTR-1/2B/3B/9/9C engines, TDS 24Q/26Q, PF/ESIC/PT, Annual Tax Compliance Pack

**Quantum Financial Services (M-F1 to M-F13):**
- F1 Portfolio Management, F2 Derivatives Pricing (Black-Scholes quantum)
- F3 VaR Monte Carlo, F4 Interest Rate Risk, F5 Loan Pricing Engine
- F6 Basel III/IV Capital Optimizer, F7 Stress Testing
- F8 Insurance Underwriting, F9 Wealth Management (HNI Robo-Advisor)
- F10 Debt Scheduling, F11 Interbank Settlement, F12 FX Exposure
- F13 AI Risk Officer Agent

### Quantum Stubs (to replace with real backends):
- `_quantum_qubo_solve()` → D-Wave Ocean SDK / EmbeddingComposite
- `_quantum_qsvr_forecast()` → Qiskit Machine Learning QSVR
- `_quantum_monte_carlo()` → Grover Amplitude Estimation (Qiskit)
- `_pqc_sign()` → liboqs-python ML-DSA (NIST FIPS 204)

---

## MASTER PROMPT — COMPLETE SYSTEM BUILD

You are a **Senior Full-Stack Architect** specialising in FinTech, quantum computing integrations, and enterprise Python platforms. Your task is to extend `spoorthy_finance_complete.py` into a **complete, production-ready system** by adding every missing layer listed below. Implement all components fully — no placeholder comments, no TODOs, no ellipsis (`...`). Every function must execute end-to-end.

---

## PART 1 — MISSING BACKEND COMPLETIONS

### 1.1 — Fix All Truncated / Stub Methods

Scan the file for every method that returns hardcoded dummy data, has TODO/stub comments, or uses `random.randint` as a placeholder for real computation. Complete each one with full business logic. Specific targets:

```
QuantumReconciliationEngine.reconcile()          — replace stub QUBO with real Ocean SDK QUBO
WorkingCapitalOptimizer.optimize()               — add real constraint propagation
FinancialStatementGenerator.generate_cash_flow() — implement indirect method fully
TransferPricingEngine._compute_alr()             — add real CUP and TNMM logic
QuantumBadDebtProvisioning.compute_ecl()         — implement full IFRS 9 three-stage ECL with PD/LGD/EAD
QuantumPayrollOptimizer                          — add full 80C/80D/HRA/LTA/NPS/gratuity/PF tax shield logic
GSTR1Engine                                      — add HSN summary auto-computation and e-invoice JSON schema
PortfolioManager.rebalance()                     — implement mean-variance optimisation (Markowitz) as QUBO
DerivativesPricingEngine                         — add Greeks (Delta, Gamma, Vega, Theta, Rho) computation
StressTestingModule                              — add contagion/network cascade stress scenarios
AIRiskOfficerAgent                               — add full NLP-to-action pipeline using internal module calls
```

### 1.2 — Add These Missing Backend Modules

#### M-A13: Quantum Budget vs Actual Engine
```
Class: BudgetActualEngine
- load_budget(entity_id, period, account_budgets: Dict[str, float])
- record_actual(entity_id, period, account_actuals: Dict[str, float])
- variance_report(entity_id, period) → {account, budget, actual, variance_amt, variance_pct, RAG_status}
- forecast_full_year(entity_id, months_elapsed) → quantum QSVR extrapolation
- alert_threshold(entity_id, threshold_pct=10) → list of accounts breaching threshold
```

#### M-A14: Fixed Asset & Depreciation Engine
```
Class: FixedAssetEngine
- capitalise(asset_id, description, cost, date_of_purchase, useful_life_years, residual_value, method)
  Methods: SLM | WDV | Units-of-Production | IFRS 16 ROU
- compute_depreciation(asset_id, period) → depreciation_charge, NBV, accumulated_depreciation
- impairment_test(asset_id, recoverable_amount) → impairment_loss or None  [Ind AS 36]
- revaluation(asset_id, fair_value) → revaluation_surplus (OCI) or deficit (P&L)  [Ind AS 16]
- disposal(asset_id, disposal_proceeds) → gain_or_loss
- generate_asset_register() → full schedule with all assets, NBV, depreciation to date
- lease_liability_schedule(lease_id, payments, rate, start_date) → IFRS 16 amortisation table
```

#### M-A15: Inventory Valuation Engine
```
Class: InventoryEngine
- receive_stock(sku, qty, unit_cost, date, supplier)
- issue_stock(sku, qty, date, job_or_cost_centre)
- valuation(sku, method) → closing_stock_value
  Methods: FIFO | LIFO | Weighted Average | Standard Cost
- stock_take(sku, physical_qty) → shortage_or_surplus, adjustment_entry
- slow_moving_report(days_threshold=180) → slow-moving SKUs with value
- abc_analysis() → A/B/C classification by value (80/15/5 rule)
- eoq(sku, annual_demand, ordering_cost, holding_cost_pct) → EOQ, reorder_point, safety_stock
```

#### M-A16: Revenue Recognition Engine (Ind AS 115 / IFRS 15)
```
Class: RevenueRecognitionEngine
- create_contract(contract_id, customer, total_value, performance_obligations: List[Dict])
- allocate_transaction_price(contract_id) → allocated_price_per_PO (relative SSP method)
- recognise_revenue(contract_id, po_id, completion_pct_or_event) → revenue_recognised, deferred_balance
- unbilled_revenue_schedule(contract_id) → month-by-month recognition schedule
- contract_modifications(contract_id, new_po, new_price) → cumulative catch-up or prospective
- generate_disclosure(contract_id) → IFRS 15 para 113-122 disclosure table
```

#### M-F14: Quantum Credit Scoring Engine
```
Class: CreditScoringEngine
- score_individual(applicant: Dict) → CIBIL-style score (300-900), risk_grade, PD
- score_corporate(company: Dict) → Altman Z-score + quantum ensemble
- recommend_loan(applicant_score, loan_amount, tenure_months) → approve/reject, max_amount, rate
- portfolio_credit_risk(loans: List[Dict]) → expected_loss, unexpected_loss, economic_capital
```

#### M-F15: Quantum Treasury Management System
```
Class: TreasuryManagementSystem
- cash_position(accounts: List[Dict]) → net_cash_position, projected_7d, projected_30d
- invest_surplus(available_cash, horizon_days, risk_appetite) → optimal_investment_mix
  Instruments: O/N call money, T-Bills, CP, CD, Liquid MF, FD
- fund_deficit(required_amount, horizon_days) → cheapest_funding_mix
- fx_hedging_recommendation(exposures: List[Dict]) → forward_contracts, options, natural_hedge
- liquidity_coverage_ratio(hqla, net_cash_outflows_30d) → LCR, Basel III compliance
- net_stable_funding_ratio(available_sf, required_sf) → NSFR, compliance
```

---

## PART 2 — DATA LAYER

### 2.1 — Database Schema (PostgreSQL)

Generate `schema.sql` with these tables (full DDL):

```sql
entities, journal_entries, journal_lines, chart_of_accounts,
bank_transactions, invoices, fixed_assets, inventory,
employees, payroll_runs, loans, portfolios,
audit_log, quantum_jobs, gst_returns
```

Include: indexes on all FK and date columns, row-level security (RLS) per entity_id, JSONB columns for quantum result storage, range partitioning on `journal_entries` by period.

### 2.2 — SQLAlchemy ORM Models (`models.py`)

- SQLAlchemy 2.0 DeclarativeBase model per table
- All relationships (one-to-many, many-to-many)
- Pydantic v2 schema alongside each ORM model
- Alembic migration `migrations/001_initial.py`

### 2.3 — Repository Pattern (`repositories.py`)

```
JournalRepository, InvoiceRepository, ReconciliationRepository,
AssetRepository, PayrollRepository, PortfolioRepository, AuditRepository
```
Each method: typed parameters, typed returns, DB session management, custom exceptions.

### 2.4 — Seed Data Script (`seed_data.py`)

- 3 demo entities: Spoorthy Technologies Pvt Ltd (India), Spoorthy UK Ltd, Spoorthy Singapore Pte
- 200+ chart of accounts
- 12 months of journal entries (FY 2025-26) for India entity
- 50 employees with complete payroll data
- 20 fixed assets (computers, furniture, vehicles, software licences)
- 100 SKU inventory records
- 5 loan facilities
- 10-stock portfolio with historical prices
- 500 bank transactions (mix of reconciled and unreconciled)
- 200 GST invoices (B2B and B2CS mix)

---

## PART 3 — REST API BACKEND (FastAPI)

### 3.1 — Structure
```
api/main.py, api/routers/{accounting,financial,compliance,reports,admin}.py
api/dependencies.py, api/middleware.py, api/exceptions.py
```

### 3.2 — Required Endpoints

**Accounting:** reconcile, journal, trial-balance, consolidate, statements, payroll/run, assets/capitalise, assets/register, inventory/receive, inventory/abc

**Financial Services:** portfolio/rebalance, derivatives/price, risk/var, risk/stress-test, treasury/position, credit/score, loan/schedule

**Compliance:** gst/gstr1, gst/gstr3b, gst/reconcile-2b, tds/26q, payroll/ecr, compliance status calendar

**Reports:** dashboard KPIs, MCA financials, audit-trail export, Excel download, PDF report

### 3.3 — Auth & Security
- JWT with refresh tokens
- Per-entity RBAC: roles = [ADMIN, ACCOUNTANT, AUDITOR, VIEWER, CFO]
- Rate limiting: 100 req/min per user
- X-PQC-Signature header on all responses
- API keys for M2M quantum job submissions

---

## PART 4 — FRONTEND (React + TypeScript + Tailwind CSS)

### 4.1 — Project Structure
```
frontend/src/
  components/{layout,charts,tables,forms,quantum}/
  pages/{Dashboard, accounting/*, financial/*, compliance/*, admin/*}
  hooks/{useQuantumJob, useEntityData, useAuth}
  store/ (Zustand)
  api/ (axios + react-query)
  utils/ (formatINR, formatDate, downloadExcel)
```

### 4.2 — Dashboard Page
KPI cards: Revenue MTD, P&L YTD, Cash Position, Working Capital, VaR 95%, Open Reconciliation Items. Revenue vs Expense 12-month bar chart. Compliance calendar with RAG status. Quantum job queue with live polling. Entity selector. Dark/light mode.

### 4.3 — Reconciliation Page
Upload bank statement CSV + open items CSV. "Run Quantum Reconciliation" button with QUBO animation. Matched pairs table, unmatched items, match rate gauge, energy display. One-click post to ledger.

### 4.4 — Financial Statements Page
Period + standard selector. Interactive P&L expandable tree. Balance Sheet with drill-down. Cash Flow waterfall chart. Export Excel/PDF.

### 4.5 — GST Compliance Page
GSTR-1 data entry, GSTR-2B ITC reconciliation with colour coding, GSTR-3B computation, filing status calendar, e-Invoice with QR code preview.

### 4.6 — Portfolio & Risk Page
Holdings table with live P&L. Asset allocation donut chart. VaR gauge. "Rebalance" QUBO solve with recommended trades. Stress test scenario selector.

---

## PART 5 — LOGGING, MONITORING & OBSERVABILITY

### 5.1 — Structured Logging (`logging_config.py`)

Use `structlog` for JSON logs. Fields: timestamp, level, module, entity_id, user_id, request_id, duration_ms, quantum_solver, qubo_energy. Separate files: app.log, audit.log, quantum.log, error.log. 100MB rotation, 30-day retention. Mask PII (PAN, GSTIN, account numbers) in all logs.

Decorators:
- `@log_module_call` — logs entry/exit + duration for every module method
- `@log_quantum_job` — logs QUBO size, solver, energy, solve_time_ms
- `@log_compliance_event` — logs all GST/TDS events with period and ARN
- `@audit_log` — posts to QuantumImmutableLedger + audit_log DB table

### 5.2 — Metrics & Alerting (`monitoring.py`)

Prometheus metrics:
```
quantum_jobs_total (Counter), quantum_solve_time_seconds (Histogram),
api_requests_total (Counter), api_latency_seconds (Histogram),
reconciliation_match_rate (Gauge), journal_entries_posted (Counter),
compliance_due_dates (Gauge: days until due)
```

Alert rules for Alertmanager (YAML):
- QuantumSolveTimeHigh (>30s → PagerDuty)
- ReconciliationMatchRateLow (<80% → Slack)
- ComplianceDueDateAlert (≤3 days → Email + Slack)
- JournalImbalance (debit ≠ credit → Critical PagerDuty)
- APIErrorRateHigh (5xx > 1% → Slack warning)

### 5.3 — Health Check Endpoint
```
GET /health → {status, db, quantum_solver, pqc_signing, last_journal_posted,
               pending_reconciliations, compliance_items_overdue, version}
```

---

## PART 6 — SCRIPTS & AUTOMATION

### 6.1 — CLI (`scripts/manage.py`) using Click
```
db init, db migrate, entity create, payroll run --period,
gst generate-gstr1, gst file-gstr3b, reconcile --bank-file --items-file,
report pnl --format excel, quantum-test, compliance-calendar, audit-export
```

### 6.2 — Scheduler (`scripts/scheduler.py`) using APScheduler
```
Daily 00:01 IST:  auto_reconcile_all_entities()
Daily 09:00 IST:  compliance_due_date_checker() → alerts
Monthly 1st 02:00: perpetual_close_trigger(), payroll_auto_run(), depreciation_auto_post()
Real-time (on journal post): qubo_reconciliation_trigger() if >50 new bank items
Weekly Sunday 01:00: portfolio_rebalance_check(), var_compute()
```

### 6.3 — Export Scripts (`scripts/exports.py`)
```
export_trial_balance_excel(entity_id, period) → .xlsx
export_gstr1_json(entity_id, period) → GSTN API JSON
export_form16a_pdf(entity_id, deductee_pan, fy) → PDF
export_audit_trail_csv(entity_id, from_date, to) → .csv
export_cbcr_xml(group_id, fy) → OECD XML
export_mca_financials_xbrl(entity_id, fy) → MCA XBRL
```

### 6.4 — Test Suite (`tests/`)
```
test_reconciliation.py   (20 cases: exact, many-to-many, tolerance, zero items)
test_financial_stmt.py   (P&L balances, BS equation, CF reconciliation)
test_gst_engine.py       (CGST/SGST/IGST computation, HSN summary, e-Invoice)
test_payroll.py          (HRA exemption, NPS, TDS new vs old regime)
test_portfolio.py        (VaR bounds, rebalancing logic, Greeks sign)
test_ecl.py              (IFRS 9 three-stage PD/LGD/EAD)
test_api.py              (FastAPI test client all endpoints)
test_quantum_stubs.py    (stub outputs within expected ranges)
conftest.py              (fixtures: in-memory DB, demo entity, sample data)
```

---

## PART 7 — DEVOPS & DEPLOYMENT

### 7.1 — Docker Compose (`docker-compose.yml`)
Services: api (FastAPI + Gunicorn + Uvicorn), frontend (React + Nginx), db (PostgreSQL 16 + pgvector), redis (session + job queue), celery (async quantum jobs), prometheus, grafana (pre-configured dashboards), flower (Celery UI)

### 7.2 — Environment Configuration (`.env.example`)
```
DATABASE_URL, DWAVE_API_TOKEN, DWAVE_ENDPOINT, IBM_QUANTUM_TOKEN,
LIBOQS_ML_DSA_PRIVATE_KEY_PATH, GSTN_CLIENT_ID, GSTN_CLIENT_SECRET,
OPEN_EXCHANGE_RATES_APP_ID, JWT_SECRET_KEY, JWT_ALGORITHM,
SLACK_WEBHOOK_URL, PAGERDUTY_ROUTING_KEY, SMTP_HOST, ALERT_EMAIL
```

---

## EXECUTION INSTRUCTIONS FOR AI

When implementing, follow this order:

1. **Read** the full existing `spoorthy_finance_complete.py` — understand all class names, method signatures, data formats, and conventions (`_now_iso()`, `_uid()`, `_pqc_sign()`, INR currency, Ind AS standards).

2. **Extend** the existing file — do not rewrite working code. Add new modules at the bottom, after `run_demo_part5()`.

3. **Add** `run_demo_all()` calling every module (existing + new) with realistic Indian business data.

4. **Maintain** existing conventions:
   - All monetary amounts in INR unless multi-currency context
   - GST rates: 5% / 12% / 18% / 28%
   - Indian fiscal year: April to March
   - Company: Spoorthy Technologies Pvt Ltd, GSTIN: 27AABCS1234C1Z1, PAN: AABCS1234C, TAN: MUMC12345E

5. **Implement** every database model with full field validation.

6. **Generate** all frontend components with TypeScript types — no `any` types.

7. **Test** all outputs — every function must return a valid, non-empty Dict or List.

8. **Document** every class with a docstring: business purpose, regulatory basis (IAS/Ind AS/GST Act/Income Tax Act section), and quantum speedup rationale.

---

## DELIVERABLES CHECKLIST

- [ ] `spoorthy_finance_complete_v2.py` — original + missing modules (M-A13 to M-A16, M-F14, M-F15) + completed stubs
- [ ] `schema.sql` — full PostgreSQL schema with RLS, indexes, partitioning
- [ ] `models.py` — SQLAlchemy 2.0 ORM + Pydantic v2 schemas
- [ ] `repositories.py` — repository pattern, all CRUD
- [ ] `seed_data.py` — demo data for 3 entities
- [ ] `api/main.py` + all routers — FastAPI with all endpoints, auth, rate limiting
- [ ] `frontend/` — React + TypeScript + Tailwind, all pages
- [ ] `logging_config.py` — structlog, JSON, PII masking, rotation
- [ ] `monitoring.py` — Prometheus metrics + alert rules YAML
- [ ] `scripts/manage.py` — Click CLI
- [ ] `scripts/scheduler.py` — APScheduler jobs
- [ ] `scripts/exports.py` — Excel/PDF/JSON/XBRL exports
- [ ] `tests/` — 100+ test cases
- [ ] `docker-compose.yml` + `Dockerfile` per service
- [ ] `.env.example` — all variables documented
- [ ] `README.md` — architecture diagram, setup guide, API reference

---

*End of Master Prompt — Spoorthy Quantum OS v1.0*
*Generated from analysis of spoorthy_finance_complete.py (11,163 lines, 25 modules)*
