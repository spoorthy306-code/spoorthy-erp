# SPOORTHY QUANTUM OS — API Routers
# Main API router including all endpoints

from fastapi import APIRouter

from .endpoints import (admin, bank_transactions, chart_of_accounts,
                        compliance, credit, employees, entities, fixed_assets,
                        gst_returns, inventory, invoices, journal_entries,
                        loans, payroll, portfolios, quantum_jobs, reports,
                        revenue, treasury)

api_router = APIRouter()

# Core entity & accounting
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(
    chart_of_accounts.router, prefix="/chart-of-accounts", tags=["chart-of-accounts"]
)
api_router.include_router(
    journal_entries.router, prefix="/journal-entries", tags=["journal-entries"]
)
api_router.include_router(
    bank_transactions.router, prefix="/bank-transactions", tags=["bank-transactions"]
)
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(
    fixed_assets.router, prefix="/fixed-assets", tags=["fixed-assets"]
)
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

# HR & Payroll
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["payroll"])

# Finance
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])

# Quantum & Compliance
api_router.include_router(
    quantum_jobs.router, prefix="/quantum-jobs", tags=["quantum-jobs"]
)
api_router.include_router(
    gst_returns.router, prefix="/gst-returns", tags=["gst-returns"]
)
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# New dedicated routers (IFRS 15, Treasury, Credit)
api_router.include_router(revenue.router, prefix="/revenue", tags=["revenue"])
api_router.include_router(treasury.router, prefix="/treasury", tags=["treasury"])
api_router.include_router(credit.router, prefix="/credit", tags=["credit"])

# Alias routers for audit-required prefixes
# /reconciliation → quantum-jobs reconciliation subset
api_router.include_router(
    quantum_jobs.router, prefix="/reconciliation", tags=["reconciliation"]
)
# /financial-statements → reports
api_router.include_router(
    reports.router, prefix="/financial-statements", tags=["financial-statements"]
)
# /risk → portfolios (VaR, risk metrics)
api_router.include_router(portfolios.router, prefix="/risk", tags=["risk"])
# /budget → reports (budget vs actual)
api_router.include_router(reports.router, prefix="/budget", tags=["budget"])
