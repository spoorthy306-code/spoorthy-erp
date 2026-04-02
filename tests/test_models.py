# SPOORTHY QUANTUM OS — Database Models Tests
# tests/test_models.py

import os
import sys
import uuid
from datetime import date, datetime

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.models.models import (EmployeeCreateSchema, Entity,
                                       EntityCreateSchema, FixedAsset,
                                       FixedAssetCreateSchema, GSTReturn,
                                       Inventory, InventoryCreateSchema,
                                       Invoice, InvoiceCreateSchema,
                                       JournalEntry, JournalEntryCreateSchema,
                                       JournalLine, LoanCreateSchema,
                                       QuantumJob)


@pytest.mark.unit
class TestEntityPydanticSchema:
    """Test Entity Pydantic schema validation"""

    def test_entity_create_valid(self):
        schema = EntityCreateSchema(
            name="Test Technologies Pvt Ltd",
            gstin="27AABCS1234C1Z1",
            pan="AABCS1234C",
            tan="MUMB12345A",
        )
        assert schema.name == "Test Technologies Pvt Ltd"
        assert schema.gstin == "27AABCS1234C1Z1"
        assert schema.currency == "INR"

    def test_entity_gstin_validation_invalid(self):
        with pytest.raises(Exception):
            EntityCreateSchema(
                name="Test Company",
                gstin="INVALID",
            )

    def test_entity_pan_validation_invalid(self):
        with pytest.raises(Exception):
            EntityCreateSchema(
                name="Test Company",
                pan="INVALID",
            )

    def test_entity_default_currency(self):
        schema = EntityCreateSchema(name="Test Company")
        assert schema.currency == "INR"
        assert schema.reporting_currency == "INR"


@pytest.mark.unit
class TestJournalEntryPydanticSchema:
    """Test JournalEntry Pydantic schema validation"""

    def test_journal_entry_balanced(self):
        schema = JournalEntryCreateSchema(
            entity_id=uuid.uuid4(),
            entry_date=date(2024, 3, 15),
            narration="Test entry",
            lines=[
                {"account_code": "1001", "debit": 100000, "credit": 0},
                {"account_code": "4001", "debit": 0, "credit": 100000},
            ],
        )
        assert len(schema.lines) == 2

    def test_journal_entry_unbalanced_raises(self):
        with pytest.raises(Exception):
            JournalEntryCreateSchema(
                entity_id=uuid.uuid4(),
                entry_date=date(2024, 3, 15),
                lines=[
                    {"account_code": "1001", "debit": 100000, "credit": 0},
                    {"account_code": "4001", "debit": 0, "credit": 50000},
                ],
            )


@pytest.mark.unit
class TestInvoicePydanticSchema:
    """Test Invoice Pydantic schema validation"""

    def test_invoice_create_valid(self):
        schema = InvoiceCreateSchema(
            entity_id=uuid.uuid4(),
            invoice_no="INV001",
            invoice_date=date(2024, 3, 15),
            buyer_name="Test Customer",
            total_amount=118000.00,
            tax_amount=18000.00,
        )
        assert schema.invoice_no == "INV001"
        assert schema.total_amount == 118000.00

    def test_invoice_negative_amount_raises(self):
        with pytest.raises(Exception):
            InvoiceCreateSchema(
                entity_id=uuid.uuid4(),
                invoice_no="INV001",
                invoice_date=date(2024, 3, 15),
                buyer_name="Test Customer",
                total_amount=-1000.00,
                tax_amount=0,
            )


@pytest.mark.unit
class TestFixedAssetPydanticSchema:
    """Test FixedAsset Pydantic schema validation"""

    def test_fixed_asset_create_valid(self):
        schema = FixedAssetCreateSchema(
            entity_id=uuid.uuid4(),
            asset_code="ASSET001",
            description="Computer System",
            cost=50000.00,
            depreciation_method="SLM",
            useful_life_years=5,
            residual_value=5000.00,
        )
        assert schema.cost == 50000.00
        assert schema.useful_life_years == 5

    def test_fixed_asset_zero_cost_raises(self):
        with pytest.raises(Exception):
            FixedAssetCreateSchema(
                entity_id=uuid.uuid4(),
                asset_code="ASSET001",
                cost=0,
                useful_life_years=5,
            )


@pytest.mark.unit
class TestInventoryPydanticSchema:
    """Test Inventory Pydantic schema validation"""

    def test_inventory_create_valid(self):
        schema = InventoryCreateSchema(
            sku="ITEM001",
            entity_id=uuid.uuid4(),
            description="Laptop",
            qty_on_hand=10,
            unit_cost=50000.00,
            costing_method="FIFO",
        )
        assert schema.sku == "ITEM001"
        assert schema.qty_on_hand == 10

    def test_inventory_negative_cost_raises(self):
        with pytest.raises(Exception):
            InventoryCreateSchema(
                sku="ITEM001", entity_id=uuid.uuid4(), qty_on_hand=10, unit_cost=-100.00
            )


@pytest.mark.unit
class TestEmployeePydanticSchema:
    """Test Employee Pydantic schema validation"""

    def test_employee_create_valid(self):
        schema = EmployeeCreateSchema(
            entity_id=uuid.uuid4(),
            name="John Doe",
            pan="ABCDE1234F",
            basic_salary=50000.00,
            hra=20000.00,
            joined_date=date(2024, 1, 1),
        )
        assert schema.name == "John Doe"
        assert schema.basic_salary == 50000.00


@pytest.mark.unit
class TestLoanPydanticSchema:
    """Test Loan Pydantic schema validation"""

    def test_loan_create_valid(self):
        schema = LoanCreateSchema(
            entity_id=uuid.uuid4(),
            facility_type="Term Loan",
            bank="HDFC Bank",
            sanctioned_amount=5000000.00,
            rate_pct=9.5,
            tenure_months=60,
            disbursement_date=date(2024, 1, 1),
        )
        assert schema.sanctioned_amount == 5000000.00
        assert schema.rate_pct == 9.5


@pytest.mark.unit
class TestGSTReturnSchema:
    """Test GSTReturn Pydantic schema"""

    def test_gst_return_create_valid(self):
        from backend.app.models.models import GSTReturnCreateSchema

        schema = GSTReturnCreateSchema(
            entity_id=uuid.uuid4(), return_type="GSTR1", period="2024-03"
        )
        assert schema.return_type == "GSTR1"
        assert schema.period == "2024-03"


# Integration tests (require DB)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_entity_create_and_retrieve(test_session, test_utils):
    """Test creating and retrieving an entity"""
    entity = await test_utils.create_test_entity(test_session)
    assert entity.entity_id is not None
    assert entity.name == "Test Technologies Pvt Ltd"
    assert entity.gstin == "27AABCS1234C1Z1"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_journal_entry_create(test_session, test_utils):
    """Test creating a journal entry"""
    entry = await test_utils.create_test_journal_entry(test_session)
    assert entry.entry_id is not None
    assert entry.total_debit == entry.total_credit


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invoice_create(test_session, test_utils):
    """Test creating an invoice"""
    invoice = await test_utils.create_test_invoice(test_session)
    assert invoice.invoice_id is not None
    assert invoice.total_amount == 118000.00
