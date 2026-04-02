# SPOORTHY QUANTUM OS — Seed Data
# Demo data for 3 entities with realistic Indian business scenarios

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import date, datetime
from ..models.models import (
    Entity, ChartOfAccount, JournalEntry, JournalLine, BankTransaction,
    Invoice, FixedAsset, Inventory, Employee, PayrollRun, Loan,
    Portfolio, QuantumJob, GSTReturn
)

async def seed_database(session: AsyncSession):
    """Seed database with demo data for 3 entities"""

    # Entity 1: Spoorthy Technologies Pvt Ltd
    entity1 = Entity(
        entity_id=uuid4(),
        name="Spoorthy Technologies Pvt Ltd",
        gstin="27AABCS1234C1Z1",
        pan="AABCS1234C",
        tan="PUNE12345C",
        address={
            "line1": "123 Tech Park, Hinjewadi",
            "city": "Pune",
            "state": "Maharashtra",
            "pincode": "411057"
        },
        currency="INR",
        reporting_currency="INR"
    )

    # Entity 2: Quantum Solutions LLP
    entity2 = Entity(
        entity_id=uuid4(),
        name="Quantum Solutions LLP",
        gstin="27AABFQ5678D2Z2",
        pan="AABFQ5678D",
        tan="MUMB12345F",
        address={
            "line1": "456 Quantum Tower, Bandra",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400051"
        },
        currency="INR",
        reporting_currency="INR"
    )

    # Entity 3: Finance Corp Ltd
    entity3 = Entity(
        entity_id=uuid4(),
        name="Finance Corp Ltd",
        gstin="27AAFCQ9012E3Z3",
        pan="AAFCQ9012E",
        tan="DELH12345G",
        address={
            "line1": "789 Finance Plaza, Connaught Place",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110001"
        },
        currency="INR",
        reporting_currency="INR"
    )

    session.add_all([entity1, entity2, entity3])
    await session.commit()

    # Chart of Accounts for Entity 1
    coa_data = [
        # Assets
        ("1001", "Cash in Hand", "Asset", None, 1),
        ("1002", "Bank Account - HDFC", "Asset", None, 1),
        ("1101", "Accounts Receivable", "Asset", None, 1),
        ("1201", "Inventory", "Asset", None, 1),
        ("1301", "Fixed Assets", "Asset", None, 1),
        ("130101", "Computers", "Asset", "1301", 2),
        ("130102", "Furniture", "Asset", "1301", 2),
        ("130103", "Software", "Asset", "1301", 2),

        # Liabilities
        ("2001", "Accounts Payable", "Liability", None, 1),
        ("2101", "GST Payable", "Liability", None, 1),
        ("2201", "Loans", "Liability", None, 1),

        # Equity
        ("3001", "Share Capital", "Equity", None, 1),
        ("3101", "Retained Earnings", "Equity", None, 1),

        # Revenue
        ("4001", "Software Services", "Revenue", None, 1),
        ("4101", "Consulting Fees", "Revenue", None, 1),

        # Expenses
        ("5001", "Salaries", "Expense", None, 1),
        ("5101", "Rent", "Expense", None, 1),
        ("5201", "Utilities", "Expense", None, 1),
        ("5301", "Depreciation", "Expense", None, 1),
        ("5401", "Professional Fees", "Expense", None, 1),
    ]

    coa_entities = []
    for code, name, typ, parent, level in coa_data:
        coa_entities.append(ChartOfAccount(
            account_code=code,
            entity_id=entity1.entity_id,
            account_name=name,
            account_type=typ,
            parent_code=parent,
            level=level,
            is_active=True
        ))

    session.add_all(coa_entities)
    await session.commit()

    # Journal Entries for Entity 1
    je1 = JournalEntry(
        entry_id=uuid4(),
        entity_id=entity1.entity_id,
        entry_date=date(2024, 4, 1),
        period="2024-04",
        narration="Opening balances",
        total_debit=1000000.00,
        total_credit=1000000.00,
        posted_by="System"
    )

    je_lines1 = [
        JournalLine(entry_id=je1.entry_id, account_code="1002", debit=500000.00, description="Bank balance"),
        JournalLine(entry_id=je1.entry_id, account_code="130101", debit=300000.00, description="Computers"),
        JournalLine(entry_id=je1.entry_id, account_code="130102", debit=100000.00, description="Furniture"),
        JournalLine(entry_id=je1.entry_id, account_code="130103", debit=100000.00, description="Software"),
        JournalLine(entry_id=je1.entry_id, account_code="3001", credit=500000.00, description="Share capital"),
        JournalLine(entry_id=je1.entry_id, account_code="2201", credit=500000.00, description="Opening loan"),
    ]

    je2 = JournalEntry(
        entry_id=uuid4(),
        entity_id=entity1.entity_id,
        entry_date=date(2024, 4, 15),
        period="2024-04",
        narration="Invoice #INV001 - Software development",
        total_debit=118000.00,
        total_credit=118000.00,
        posted_by="System"
    )

    je_lines2 = [
        JournalLine(entry_id=je2.entry_id, account_code="1101", debit=118000.00, description="Client invoice"),
        JournalLine(entry_id=je2.entry_id, account_code="4001", credit=100000.00, description="Software services"),
        JournalLine(entry_id=je2.entry_id, account_code="2101", credit=18000.00, description="GST @18%"),
    ]

    session.add_all([je1, je2] + je_lines1 + je_lines2)
    await session.commit()

    # Bank Transactions
    bank_txns = [
        BankTransaction(
            txn_id=uuid4(),
            entity_id=entity1.entity_id,
            bank_account="HDFC-1234",
            txn_date=date(2024, 4, 1),
            description="Opening balance",
            amount=500000.00,
            balance=500000.00,
            reconciled=True,
            reconciled_entry_id=je1.entry_id
        ),
        BankTransaction(
            txn_id=uuid4(),
            entity_id=entity1.entity_id,
            bank_account="HDFC-1234",
            txn_date=date(2024, 4, 16),
            description="Client payment - INV001",
            amount=118000.00,
            balance=618000.00,
            reconciled=False
        ),
    ]

    session.add_all(bank_txns)
    await session.commit()

    # Invoices
    invoices = [
        Invoice(
            invoice_id=uuid4(),
            entity_id=entity1.entity_id,
            invoice_no="INV001",
            invoice_date=date(2024, 4, 15),
            buyer_gstin="27AAABC5678F1Z5",
            buyer_name="Tech Solutions Pvt Ltd",
            total_amount=118000.00,
            tax_amount=18000.00,
            status="ACTIVE"
        ),
    ]

    session.add_all(invoices)
    await session.commit()

    # Fixed Assets
    fixed_assets = [
        FixedAsset(
            asset_id=uuid4(),
            entity_id=entity1.entity_id,
            asset_code="COMP001",
            description="Dell Laptop",
            cost=75000.00,
            accumulated_depreciation=7500.00,
            nbv=67500.00,
            depreciation_method="SLM",
            useful_life_years=5,
            residual_value=0.00,
            status="ACTIVE"
        ),
        FixedAsset(
            asset_id=uuid4(),
            entity_id=entity1.entity_id,
            asset_code="FURN001",
            description="Office Furniture",
            cost=50000.00,
            accumulated_depreciation=5000.00,
            nbv=45000.00,
            depreciation_method="SLM",
            useful_life_years=10,
            residual_value=0.00,
            status="ACTIVE"
        ),
    ]

    session.add_all(fixed_assets)
    await session.commit()

    # Inventory
    inventory_items = [
        Inventory(
            sku="SOFT001",
            entity_id=entity1.entity_id,
            description="Custom Software License",
            qty_on_hand=10.00,
            unit_cost=5000.00,
            total_value=50000.00,
            costing_method="FIFO"
        ),
    ]

    session.add_all(inventory_items)
    await session.commit()

    # Employees
    employees = [
        Employee(
            employee_id=uuid4(),
            entity_id=entity1.entity_id,
            name="Rajesh Kumar",
            pan="ABCDE1234F",
            uan="MH123456789",
            basic_salary=50000.00,
            hra=10000.00,
            lta=5000.00,
            medical=2500.00,
            nps=2500.00,
            pf_employee=1800.00,
            joined_date=date(2023, 1, 1),
            status="ACTIVE"
        ),
    ]

    session.add_all(employees)
    await session.commit()

    # Payroll Run
    payroll_run = PayrollRun(
        run_id=uuid4(),
        entity_id=entity1.entity_id,
        period="2024-04",
        total_gross=67500.00,
        total_deductions=4300.00,
        total_net=63200.00,
        pf_employer=1800.00,
        esic_employer=405.00,
        pt=235.00,
        tds=1200.00
    )

    session.add(payroll_run)
    await session.commit()

    # Loans
    loans = [
        Loan(
            loan_id=uuid4(),
            entity_id=entity1.entity_id,
            facility_type="Term Loan",
            bank="HDFC Bank",
            sanctioned_amount=500000.00,
            outstanding=450000.00,
            rate_pct=12.50,
            emi=12000.00,
            tenure_months=60,
            disbursement_date=date(2023, 4, 1),
            status="ACTIVE"
        ),
    ]

    session.add_all(loans)
    await session.commit()

    # Portfolios
    portfolios = [
        Portfolio(
            portfolio_id=uuid4(),
            entity_id=entity1.entity_id,
            name="Investment Portfolio",
            total_value=1000000.00,
            holdings=[
                {"ticker": "NIFTY", "qty": 50, "price": 18500, "value": 925000},
                {"ticker": "INFY.NS", "qty": 100, "price": 1500, "value": 150000}
            ]
        ),
    ]

    session.add_all(portfolios)
    await session.commit()

    # Quantum Jobs
    quantum_jobs = [
        QuantumJob(
            job_id=uuid4(),
            entity_id=entity1.entity_id,
            module="Reconciliation",
            solver="D-Wave QUBO",
            qubo_size=100,
            energy=-45.67,
            solve_time_ms=1200,
            result={"matches": 95, "accuracy": 0.98},
            status="COMPLETED"
        ),
    ]

    session.add_all(quantum_jobs)
    await session.commit()

    # GST Returns
    gst_returns = [
        GSTReturn(
            return_id=uuid4(),
            entity_id=entity1.entity_id,
            return_type="GSTR1",
            period="2024-04",
            json_payload={
                "gstin": "27AABCS1234C1Z1",
                "fp": "042024",
                "b2b": [
                    {
                        "ctin": "27AAABC5678F1Z5",
                        "inv": [
                            {
                                "inum": "INV001",
                                "idt": "15-04-2024",
                                "val": 118000.00,
                                "itms": [
                                    {
                                        "itm_det": {
                                            "rt": 18.0,
                                            "txval": 100000.00,
                                            "iamt": 18000.00
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            status="FILED",
            arn="ARN123456789"
        ),
    ]

    session.add_all(gst_returns)
    await session.commit()

    print("Database seeded with demo data for 3 entities")