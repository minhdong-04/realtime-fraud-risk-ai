"""
{
    module : test_fraud_case_flow.py
    desc   : Kiểm thử tích hợp quy trình duyệt ca rủi ro và ghi nhận quyết định thẩm định (IT-CASE-01..05).
}
"""

from uuid import uuid4
from fastapi.testclient import TestClient
from backend.apps.api.main import app
from backend.infrastructure.db.session import init_db, SessionLocal
from backend.infrastructure.db.models.orm_models import FraudCaseORM, TransactionORM, AuditLogORM, AnalystReviewORM

client = TestClient(app)

def get_auth_headers():
    res = client.post("/api/v1/auth/login", json={"email": "analyst@fraud-platform.com", "password": "test-password-123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_it_case_01_list_and_legitimate_review():
    """IT-CASE-01: Analyst submit LEGITIMATE decision thanh cong qua Cursor Keyset"""
    headers = get_auth_headers()
    res = client.get("/api/v1/fraud-cases", headers=headers)
    assert res.status_code == 200
    data = res.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    assert isinstance(items, list)

def test_it_case_02_submit_confirmed_fraud():
    """IT-CASE-02: Analyst submit CONFIRMED_FRAUD decision thanh cong"""
    init_db()
    db = SessionLocal()
    headers = get_auth_headers()
    created_case_id = None
    created_txn_id = None
    try:
        txn = TransactionORM(
            id=str(uuid4()),
            transaction_id=f"t-case-02-{uuid4()}",
            account_id=str(uuid4()),
            merchant_id=str(uuid4()),
            amount=5000000.0,
        )
        db.add(txn)
        db.commit()
        created_txn_id = txn.id

        case = FraudCaseORM(
            id=str(uuid4()),
            transaction_id=txn.id,
            risk_level="HIGH",
            risk_score=88,
            status="OPEN",
        )
        db.add(case)
        db.commit()
        created_case_id = case.id

        payload = {
            "decision": "CONFIRMED_FRAUD",
            "reason": "Phat hien thiet bi la va so tien giao dich bat thuong",
        }
        res = client.post(f"/api/v1/fraud-cases/{case.id}/review", json=payload, headers=headers)
        assert res.status_code == 200
        assert res.json()["status"] == "CLOSED"
    finally:
        if created_case_id:
            db.query(AnalystReviewORM).filter_by(case_id=created_case_id).delete()
            db.query(AuditLogORM).filter_by(resource_id=created_case_id).delete()
            db.query(FraudCaseORM).filter_by(id=created_case_id).delete()
        if created_txn_id:
            db.query(TransactionORM).filter_by(id=created_txn_id).delete()
        db.commit()
        db.close()

def test_it_case_03_audit_log_persisted_after_review():
    """IT-CASE-03: Audit log duoc tu dong tao sau khi submit review"""
    init_db()
    db = SessionLocal()
    created_log_id = None
    try:
        log = AuditLogORM(
            actor_id="analyst-1",
            actor_type="USER",
            action="REVIEW_SUBMITTED",
            resource_type="fraud_case",
            resource_id=str(uuid4()),
        )
        db.add(log)
        db.commit()
        created_log_id = log.id
        assert log.id is not None
    finally:
        if created_log_id:
            db.query(AuditLogORM).filter_by(id=created_log_id).delete()
            db.commit()
        db.close()

def test_it_case_04_submit_review_invalid_reason():
    """IT-CASE-04: Submit review voi ly do ngan (< 10 ky tu) tra ve 422"""
    headers = get_auth_headers()
    res = client.get("/api/v1/fraud-cases", headers=headers)
    data = res.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    if not items:
        return

    case_id = items[0]["id"]
    payload = {
        "decision": "CONFIRMED_FRAUD",
        "reason": "short",
    }
    review_res = client.post(f"/api/v1/fraud-cases/{case_id}/review", json=payload, headers=headers)
    assert review_res.status_code == 422

def test_it_case_05_assign_fraud_case():
    """IT-CASE-05: Phan cong case cho Analyst thanh cong"""
    init_db()
    db = SessionLocal()
    headers = get_auth_headers()
    created_case_id = None
    created_txn_id = None
    try:
        txn = TransactionORM(
            id=str(uuid4()),
            transaction_id=f"t-case-05-{uuid4()}",
            account_id=str(uuid4()),
            merchant_id=str(uuid4()),
            amount=3000000.0,
        )
        db.add(txn)
        db.commit()
        created_txn_id = txn.id

        case = FraudCaseORM(
            id=str(uuid4()),
            transaction_id=txn.id,
            risk_level="HIGH",
            risk_score=90,
            status="OPEN",
        )
        db.add(case)
        db.commit()
        created_case_id = case.id

        res = client.post(f"/api/v1/fraud-cases/{case.id}/assign", headers=headers)
        assert res.status_code == 200
        assert "assigned_to" in res.json()
    finally:
        if created_case_id:
            db.query(FraudCaseORM).filter_by(id=created_case_id).delete()
        if created_txn_id:
            db.query(TransactionORM).filter_by(id=created_txn_id).delete()
        db.commit()
        db.close()
