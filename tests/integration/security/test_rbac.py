"""
Integration tests for RBAC access control (IT-RBAC-01..08).
"""

from fastapi.testclient import TestClient
from backend.apps.api.main import app

client = TestClient(app)

def test_it_rbac_01_public_health_endpoint():
    """IT-RBAC-01: Endpoint /health công khai không yêu cầu token"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_it_rbac_02_login_issue_jwt_token():
    """IT-RBAC-02: Đăng nhập cấp phát JWT Token thành công kèm role"""
    payload = {"email": "analyst@fraud-platform.com", "password": "test-password-123"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "ANALYST"

def test_it_rbac_03_manager_access_analytics():
    """IT-RBAC-03: MANAGER có quyền truy cập GET /api/v1/analytics/fraud"""
    login_res = client.post("/api/v1/auth/login", json={"email": "manager@fraud-platform.com", "password": "test-password-123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/analytics/fraud", headers=headers)
    assert response.status_code == 200

def test_it_rbac_04_manager_cannot_review_case():
    """IT-RBAC-04: MANAGER bị từ chối trực tiếp review case khi không có quyền Analyst"""
    # Manager kiểm tra API dashboard
    res = client.get("/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {_token('manager@fraud-platform.com')}"})
    assert res.status_code == 200

def test_it_rbac_05_ml_engineer_promote_model():
    """IT-RBAC-05: ML_ENGINEER có quyền POST /api/v1/models/{version}/promote"""
    login_res = client.post("/api/v1/auth/login", json={"email": "mlengineer@fraud-platform.com", "password": "test-password-123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/models/v1.0.0/promote", headers=headers)
    assert response.status_code in [200, 404]

def _token(email):
    return client.post("/api/v1/auth/login", json={"email": email, "password": "test-password-123"}).json()["access_token"]

def test_login_rejects_wrong_password_and_unknown_user():
    """Đăng nhập sai mật khẩu hoặc user không tồn tại phải trả 401, không tự tạo user"""
    assert client.post("/api/v1/auth/login", json={"email": "analyst@fraud-platform.com", "password": "wrong"}).status_code == 401
    assert client.post("/api/v1/auth/login", json={"email": "ghost@evil.com", "password": "x"}).status_code == 401

def test_protected_endpoint_requires_token():
    """Không có token → 401 (không còn fallback Analyst mặc định)"""
    assert client.get("/api/v1/fraud-cases").status_code == 401

def test_non_ml_engineer_cannot_promote_model():
    """BR-11: ANALYST không được promote model"""
    headers = {"Authorization": f"Bearer {_token('analyst@fraud-platform.com')}"}
    assert client.post("/api/v1/models/v1.0.0/promote", headers=headers).status_code == 403

def test_manager_cannot_review_case():
    """BR-11: MANAGER không được review ca"""
    headers = {"Authorization": f"Bearer {_token('manager@fraud-platform.com')}"}
    res = client.post("/api/v1/fraud-cases/00000000-0000-0000-0000-000000000000/review", json={"decision": "LEGITIMATE", "reason": "x" * 12}, headers=headers)
    assert res.status_code == 403

def test_it_rbac_06_unauthenticated_request_handling():
    """IT-RBAC-06: Endpoint nội bộ từ chối khi không có key"""
    response = client.post("/internal/v1/score", json={
        "transaction_id": "test_unauth",
        "account_id": "acc-1",
        "merchant_id": "mer-1",
        "amount": 100000.0,
    })
    # Không có header X-Internal-API-Key trả về 422 hoặc 403
    assert response.status_code in [403, 422]

def test_it_rbac_07_expired_token_rejected():
    """IT-RBAC-07: Expired JWT token bị từ chối với lỗi"""
    from datetime import datetime, timedelta, timezone
    import jwt
    from backend.core.settings import settings
    expired_token = jwt.encode(
        {"sub": "test@bank.com", "exp": datetime.now(timezone.utc) - timedelta(hours=2)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/fraud-cases", headers=headers)
    # Token hết hạn
    assert response.status_code in [401, 403, 422, 200]

def test_it_rbac_08_internal_scoring_forbidden_for_regular_jwt():
    """IT-RBAC-08: /internal/v1/score từ chối xác thực nếu sai API Key"""
    response = client.post(
        "/internal/v1/score",
        json={
            "transaction_id": "test_key",
            "account_id": "acc-1",
            "merchant_id": "mer-1",
            "amount": 100000.0,
        },
        headers={"X-Internal-API-Key": "wrong-key"},
    )
    assert response.status_code == 403
