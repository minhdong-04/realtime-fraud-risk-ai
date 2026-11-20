"""
{
    module : test_transaction_flow.py
    desc   : Kiểm thử tích hợp luồng nạp giao dịch qua API (IT-API-01..06).
}
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.apps.api.main import app
from backend.infrastructure.db.session import init_db, SessionLocal
from backend.infrastructure.db.models.orm_models import UserORM

client = TestClient(app)

@pytest.fixture(autouse=True)
def _authenticated_client(analyst_headers):
    client.headers.update(analyst_headers)

def test_it_api_01_submit_transaction_success():
    """IT-API-01: Gửi giao dịch hợp lệ nhận HTTP 202 ACCEPTED"""
    payload = {
        "transaction_id": f"TXN-IT-{uuid4()}",
        "account_id": str(uuid4()),
        "merchant_id": str(uuid4()),
        "amount": 1500000.0,
        "currency": "VND",
        "transaction_type": "PURCHASE",
        "channel": "WEB",
    }
    response = client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 202
    assert response.json()["status"] == "ACCEPTED"

def test_it_api_02_submit_transaction_duplicate_conflict():
    """IT-API-02: Gửi trùng transaction_id nhận HTTP 409 CONFLICT (BR-05)"""
    txn_id = f"TXN-DUP-{uuid4()}"
    payload = {
        "transaction_id": txn_id,
        "account_id": str(uuid4()),
        "merchant_id": str(uuid4()),
        "amount": 500000.0,
        "currency": "VND",
    }
    r1 = client.post("/api/v1/transactions", json=payload)
    assert r1.status_code == 202

    r2 = client.post("/api/v1/transactions", json=payload)
    assert r2.status_code == 409

def test_it_api_03_invalid_payload_validation_error():
    """IT-API-03: POST /transactions invalid payload trả về 422"""
    invalid_payload = {"transaction_id": "only_id"}
    response = client.post("/api/v1/transactions", json=invalid_payload)
    assert response.status_code == 422

def test_it_api_04_get_transaction_detail():
    """IT-API-04: GET /transactions/{id} trả về 200 kèm chi tiết giao dịch"""
    txn_id = f"TXN-GET-{uuid4()}"
    payload = {
        "transaction_id": txn_id,
        "account_id": str(uuid4()),
        "merchant_id": str(uuid4()),
        "amount": 200000.0,
        "currency": "VND",
    }
    client.post("/api/v1/transactions", json=payload)
    response = client.get(f"/api/v1/transactions/{txn_id}")
    assert response.status_code == 200
    assert response.json()["transaction_id"] == txn_id

def test_it_api_05_get_transaction_not_found():
    """IT-API-05: GET /transactions/{id} không tồn tại trả về 404"""
    response = client.get(f"/api/v1/transactions/non_existent_{uuid4()}")
    assert response.status_code == 404

def test_it_api_06_get_account_transactions():
    """IT-API-06: GET /transactions/account/{account_id} trả về lịch sử tài khoản"""
    acc_id = str(uuid4())
    payload = {
        "transaction_id": f"TXN-ACC-{uuid4()}",
        "account_id": acc_id,
        "merchant_id": str(uuid4()),
        "amount": 300000.0,
        "currency": "VND",
    }
    client.post("/api/v1/transactions", json=payload)
    response = client.get(f"/api/v1/transactions/account/{acc_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
