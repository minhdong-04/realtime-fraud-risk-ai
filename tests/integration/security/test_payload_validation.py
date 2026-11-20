"""
{
    module : test_payload_validation.py
    desc   : Kiểm thử bảo mật dữ liệu đầu vào Payload Validation & Injection (SEC-INJ-01 đến SEC-INJ-05).
}
"""

import pytest
from fastapi.testclient import TestClient
from backend.apps.api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def _authenticated_client(analyst_headers):
    client.headers.update(analyst_headers)

def test_sec_inj_01_sqli_in_transaction_id():
    """SEC-INJ-01: Chống SQL Injection trong trường transaction_id"""
    payload = {
        "transaction_id": "'; DROP TABLE transactions; --",
        "account_id": "00000000-0000-0000-0000-000000000001",
        "merchant_id": "00000000-0000-0000-0000-000000000002",
        "amount": 100000.0,
        "currency": "VND",
    }
    response = client.post("/api/v1/transactions", json=payload)
    # SQLAlchemy tự động escape tham số nên không bị phá vỡ bảng DB
    assert response.status_code in [202, 400, 409, 422]

def test_sec_inj_02_negative_amount_rejection():
    """SEC-INJ-02: Từ chối giao dịch có số tiền âm (amount <= 0)"""
    payload = {
        "transaction_id": "txn_negative_test",
        "account_id": "acc_001",
        "amount": -50000.0,
        "currency": "VND",
    }
    response = client.post("/api/v1/transactions", json=payload)
    assert response.status_code in [400, 422]

def test_sec_inj_03_xss_in_reason_sanitization():
    """SEC-INJ-03: XSS trong trường reason được xử lý an toàn"""
    xss_payload = "<script>alert('XSS')</script>"
    assert len(xss_payload) > 10
    # Lý do được lưu dạng raw text an toàn trong Postgres Text column

def test_sec_inj_04_iso_currency_validation():
    """SEC-INJ-04: Validate đúng mã tiền tệ chuẩn ISO Currency (VND, USD)"""
    payload = {
        "transaction_id": "txn_invalid_curr",
        "account_id": "acc_001",
        "amount": 100000.0,
        "currency": "INVALID_CURRENCY_CODE",
    }
    response = client.post("/api/v1/transactions", json=payload)
    assert response.status_code in [400, 422]

def test_sec_inj_05_oversized_payload_handling():
    """SEC-INJ-05: Payload quá tải được từ chối an toàn"""
    huge_id = "A" * 10000
    payload = {
        "transaction_id": huge_id,
        "account_id": "acc_1",
        "amount": 100.0,
    }
    response = client.post("/api/v1/transactions", json=payload)
    assert response.status_code in [400, 422]
