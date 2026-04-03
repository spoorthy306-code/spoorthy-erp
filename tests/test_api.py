# SPOORTHY QUANTUM OS — API Tests

import uuid

import pytest


@pytest.mark.api
class TestEntityAPI:
    def test_create_entity(self, client, sample_entity_data):
        response = client.post("/api/v1/entities/", json=sample_entity_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_entity_data["name"]
        assert data["gstin"] == sample_entity_data["gstin"]
        assert "entity_id" in data

    def test_get_entity(self, client, sample_entity_data):
        created = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.get(f"/api/v1/entities/{created['entity_id']}")
        assert response.status_code == 200
        assert response.json()["entity_id"] == created["entity_id"]

    def test_get_entities_list(self, client, sample_entity_data):
        client.post("/api/v1/entities/", json=sample_entity_data)
        response = client.get("/api/v1/entities/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_update_entity(self, client, sample_entity_data):
        created = client.post("/api/v1/entities/", json=sample_entity_data).json()
        update_data = {
            "name": "Updated Test Company",
            "gstin": sample_entity_data["gstin"],
            "pan": sample_entity_data["pan"],
            "currency": "INR",
            "reporting_currency": "INR",
        }
        response = client.put(
            f"/api/v1/entities/{created['entity_id']}", json=update_data
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Test Company"

    def test_delete_entity(self, client, sample_entity_data):
        created = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.delete(f"/api/v1/entities/{created['entity_id']}")
        assert response.status_code == 200
        assert "message" in response.json()
        response = client.get(f"/api/v1/entities/{created['entity_id']}")
        assert response.status_code == 404


@pytest.mark.api
class TestJournalEntryAPI:
    def test_create_journal_entry(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        payload = {
            "entity_id": entity["entity_id"],
            "entry_date": "2024-03-15",
            "narration": "Test journal entry",
            "lines": [
                {"account_code": "1001", "debit": 1000.0, "credit": 0.0},
                {"account_code": "4001", "debit": 0.0, "credit": 1000.0},
            ],
        }
        response = client.post("/api/v1/journal-entries/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == entity["entity_id"]
        assert data["total_debit"] == 1000.0
        assert data["total_credit"] == 1000.0

    def test_get_journal_entries(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        payload = {
            "entity_id": entity["entity_id"],
            "entry_date": "2024-03-15",
            "narration": "List test",
            "lines": [
                {"account_code": "1001", "debit": 500.0, "credit": 0.0},
                {"account_code": "4001", "debit": 0.0, "credit": 500.0},
            ],
        }
        client.post("/api/v1/journal-entries/", json=payload)
        response = client.get(
            f"/api/v1/journal-entries/?entity_id={entity['entity_id']}"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_journal_entry_by_id(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        payload = {
            "entity_id": entity["entity_id"],
            "entry_date": "2024-03-15",
            "narration": "Get by id test",
            "lines": [
                {"account_code": "1001", "debit": 250.0, "credit": 0.0},
                {"account_code": "4001", "debit": 0.0, "credit": 250.0},
            ],
        }
        created = client.post("/api/v1/journal-entries/", json=payload).json()
        response = client.get(f"/api/v1/journal-entries/{created['entry_id']}")
        assert response.status_code == 200
        assert response.json()["entry_id"] == created["entry_id"]


@pytest.mark.api
class TestInvoiceAPI:
    def test_create_invoice(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        payload = {
            "entity_id": entity["entity_id"],
            "invoice_no": f"INV-{uuid.uuid4().hex[:8].upper()}",
            "invoice_date": "2024-03-15",
            "buyer_gstin": "29AAAAA0000A1Z5",
            "buyer_name": "Test Customer",
            "total_amount": 118000.0,
            "tax_amount": 18000.0,
        }
        response = client.post("/api/v1/invoices/", json=payload)
        assert response.status_code == 200
        assert response.json()["entity_id"] == entity["entity_id"]

    def test_get_invoices(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        payload = {
            "entity_id": entity["entity_id"],
            "invoice_no": f"INV-{uuid.uuid4().hex[:8].upper()}",
            "invoice_date": "2024-03-15",
            "buyer_gstin": "29AAAAA0000A1Z5",
            "buyer_name": "Test Customer",
            "total_amount": 1000.0,
            "tax_amount": 180.0,
        }
        client.post("/api/v1/invoices/", json=payload)
        response = client.get(f"/api/v1/invoices/?entity_id={entity['entity_id']}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.api
class TestReportsAPI:
    def test_trial_balance_report(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.get(
            f"/api/v1/reports/trial-balance/{entity['entity_id']}?period=2024-03"
        )
        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert "total_debit" in data
        assert "total_credit" in data

    def test_profit_loss_report(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.get(
            f"/api/v1/reports/pnl/{entity['entity_id']}?period=2024-03"
        )
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
        assert "expenses" in data
        assert "net_profit" in data

    def test_balance_sheet_report(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.get(
            f"/api/v1/reports/balance-sheet/{entity['entity_id']}?as_of_date=2024-03-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert "liabilities" in data


@pytest.mark.api
class TestComplianceAPI:
    def test_gst_return_generation(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.post(
            f"/api/v1/compliance/gst/generate-gstr1/{entity['entity_id']}?period=2024-03"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "data" in data

    def test_compliance_status(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.get(
            f"/api/v1/compliance/compliance-status/{entity['entity_id']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data


@pytest.mark.api
class TestAdminAPI:
    def test_system_health(self, client):
        response = client.get("/api/v1/admin/system-health")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "quantum_jobs" in data

    def test_quantum_stats(self, client):
        response = client.get("/api/v1/admin/quantum-stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_solve_time_ms" in data


@pytest.mark.api
class TestAuthentication:
    def test_invalid_token(self, unauthenticated_client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = unauthenticated_client.get("/api/v1/entities/", headers=headers)
        assert response.status_code == 401

    def test_missing_token(self, unauthenticated_client):
        response = unauthenticated_client.get("/api/v1/entities/")
        assert response.status_code == 401


@pytest.mark.api
class TestQuantumAPI:
    def test_quantum_job_submit(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.post(
            f"/api/v1/quantum-jobs/submit?entity_id={entity['entity_id']}&module=Reconciliation"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["entity_id"] == entity["entity_id"]
        assert data["status"] == "COMPLETED"

    def test_quantum_portfolio_optimization(self, client, sample_entity_data):
        entity = client.post("/api/v1/entities/", json=sample_entity_data).json()
        response = client.get(
            f"/api/v1/reports/portfolio-optimization/{entity['entity_id']}?risk_tolerance=0.5"
        )
        assert response.status_code == 200
        data = response.json()
        assert "allocation" in data
        assert "expected_return" in data


@pytest.mark.api
class TestErrorHandling:
    def test_not_found_entity(self, client):
        response = client.get(f"/api/v1/entities/{uuid.uuid4()}")
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_invalid_data(self, client):
        invalid_entity = {
            "name": "Test",
            "gstin": "invalid_gstin",
            "pan": "BADPAN",
            "currency": "INR",
            "reporting_currency": "INR",
        }
        response = client.post("/api/v1/entities/", json=invalid_entity)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert len(data["detail"]) > 0

    def test_method_not_allowed(self, client):
        response = client.patch("/api/v1/entities/")
        assert response.status_code == 405
