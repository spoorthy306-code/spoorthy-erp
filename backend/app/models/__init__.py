"""Models package — canonical SQLAlchemy models (models.py)"""
# Note: importing all models here in package init can cause SQLAlchemy declarative class
# conflicts when app imports models from another schema source (e.g., db.schema). Keep
# this minimal to avoid duplicate table warning in mixed environments.

from backend.app.models.models import (
    Base,
    Entity, ChartOfAccount, JournalEntry, JournalLine,
    BankTransaction, Invoice, FixedAsset, Inventory,
    Employee, PayrollRun, Loan, Portfolio, AuditLog,
    QuantumJob, GSTReturn,
    # Pydantic schemas
    EntitySchema, EntityCreateSchema,
    JournalEntrySchema, JournalEntryCreateSchema,
    InvoiceSchema, InvoiceCreateSchema,
    BankTransactionSchema, BankTransactionCreateSchema,
    FixedAssetSchema, FixedAssetCreateSchema,
    InventorySchema, InventoryCreateSchema,
    EmployeeSchema, EmployeeCreateSchema,
    PayrollRunSchema, PayrollRunCreateSchema,
    LoanSchema, LoanCreateSchema,
    PortfolioSchema, PortfolioCreateSchema,
    QuantumJobSchema, GSTReturnSchema, GSTReturnCreateSchema,
)

__all__ = [
    'Base',
    'Entity', 'ChartOfAccount', 'JournalEntry', 'JournalLine',
    'BankTransaction', 'Invoice', 'FixedAsset', 'Inventory',
    'Employee', 'PayrollRun', 'Loan', 'Portfolio', 'AuditLog',
    'QuantumJob', 'GSTReturn',
    'EntitySchema', 'EntityCreateSchema',
    'JournalEntrySchema', 'JournalEntryCreateSchema',
    'InvoiceSchema', 'InvoiceCreateSchema',
    'BankTransactionSchema', 'BankTransactionCreateSchema',
    'FixedAssetSchema', 'FixedAssetCreateSchema',
    'InventorySchema', 'InventoryCreateSchema',
    'EmployeeSchema', 'EmployeeCreateSchema',
    'PayrollRunSchema', 'PayrollRunCreateSchema',
    'LoanSchema', 'LoanCreateSchema',
    'PortfolioSchema', 'PortfolioCreateSchema',
    'QuantumJobSchema', 'GSTReturnSchema', 'GSTReturnCreateSchema',
]
