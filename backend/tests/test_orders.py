import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_create_order():
    payload = {
        "customer_id": 1,
        "total_amount": 100.50,
        "status": "pending",
        "notes": "Test order"
    }

    response = client.post("/orders/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["customer_id"] == payload["customer_id"]
    assert float(data["total_amount"]) == pytest.approx(payload["total_amount"])
    assert data["status"] == payload["status"]
    assert data["notes"] == payload["notes"]

    # Save order id for read test
    global created_order_id
    created_order_id = data["id"]


def test_read_order():
    # Ensure create_order has already run and set created_order_id
    assert hasattr(globals(), "created_order_id")
    order_id = globals()["created_order_id"]

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["customer_id"] == 1
    assert float(data["total_amount"]) == pytest.approx(100.50)
    assert data["status"] == "pending"
    assert data["notes"] == "Test order"
