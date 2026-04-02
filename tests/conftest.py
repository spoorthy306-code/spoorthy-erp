import asyncio
import uuid
from datetime import date
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import StaticPool

from backend.app.db.session import get_db
from backend.app.main import app, get_current_active_user
from backend.app.models.models import Base, Entity, Invoice, JournalEntry

TEST_DATABASE_URL = "sqlite+aiosqlite:///./spoorthy_test.db"


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Create one event loop per test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create shared async engine and schema for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create per-test async session with rollback safety."""
    factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def client(test_session):
    """Provide FastAPI test client with DB dependency override."""

    async def _override_get_db():
        yield test_session

    async def _override_current_user():
        return "test-user"

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_active_user] = _override_current_user
    with TestClient(app, base_url="http://localhost") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def unauthenticated_client(test_session):
    """Client with DB override only; auth behavior remains real."""

    async def _override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, base_url="http://localhost") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_entity_data():
    unique_digits = f"{uuid.uuid4().int % 10000:04d}"
    return {
        "name": f"Test Technologies {unique_digits}",
        "gstin": f"27AABCS{unique_digits}C1Z1",
        "pan": f"AABCS{unique_digits}C",
        "currency": "INR",
        "reporting_currency": "INR",
    }


@pytest.fixture
def sample_journal_entry_data():
    return {
        "entity_id": str(uuid.uuid4()),
        "entry_date": str(date.today()),
        "narration": "Test journal entry",
        "lines": [
            {"account_code": "1001", "debit": 100000.0, "credit": 0.0},
            {"account_code": "4001", "debit": 0.0, "credit": 100000.0},
        ],
    }


@pytest.fixture
def sample_invoice_data():
    return {
        "entity_id": str(uuid.uuid4()),
        "invoice_no": "INV001",
        "invoice_date": str(date.today()),
        "buyer_gstin": "29AAAAA0000A1Z5",
        "buyer_name": "Test Customer",
        "total_amount": 118000.0,
        "tax_amount": 18000.0,
    }


class TestUtils:
    @staticmethod
    async def create_test_entity(
        session: AsyncSession, entity_data: dict | None = None
    ) -> Entity:
        if entity_data is None:
            entity_data = {
                "name": "Test Technologies Pvt Ltd",
                "gstin": "27AABCS1234C1Z1",
                "pan": "AABCS1234C",
                "currency": "INR",
                "reporting_currency": "INR",
            }
        entity = Entity(**entity_data)
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    @staticmethod
    async def create_test_journal_entry(
        session: AsyncSession, entry_data: dict | None = None
    ) -> JournalEntry:
        if entry_data is None:
            entity = await TestUtils.create_test_entity(session)
            entry_data = {
                "entity_id": entity.entity_id,
                "entry_date": date(2024, 3, 15),
                "period": "2024-03",
                "narration": "Test journal entry",
                "total_debit": 100000.0,
                "total_credit": 100000.0,
                "posted_by": "test_user",
            }

        entry = JournalEntry(**entry_data)
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry

    @staticmethod
    async def create_test_invoice(
        session: AsyncSession, invoice_data: dict | None = None
    ) -> Invoice:
        if invoice_data is None:
            entity = await TestUtils.create_test_entity(session)
            invoice_data = {
                "entity_id": entity.entity_id,
                "invoice_no": "INV001",
                "invoice_date": date(2024, 3, 15),
                "buyer_gstin": "29AAAAA0000A1Z5",
                "buyer_name": "Test Customer",
                "total_amount": 118000.0,
                "tax_amount": 18000.0,
                "status": "ACTIVE",
            }

        invoice = Invoice(**invoice_data)
        session.add(invoice)
        await session.commit()
        await session.refresh(invoice)
        return invoice


@pytest.fixture
def test_utils():
    return TestUtils()


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "quantum: Quantum tests")
    config.addinivalue_line("markers", "database: Database tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "slow: Slow tests")
