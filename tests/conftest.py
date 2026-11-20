"""
{
    module : conftest.py
    desc   : Cau hinh pytest va fixture khoi tao database moi truong test (Isolated SQLite).
}
"""

import os
import pytest

# Thiet lap bien moi truong test truoc khi bat ky module backend nao duoc import
os.environ["DATABASE_URL"] = "sqlite:///./test_fraud_platform.db"
os.environ["JWT_SECRET"] = "super-secret-test-key-must-be-at-least-32-bytes-long!"
TEST_PASSWORD = "test-password-123"

from backend.infrastructure.db.session import init_db, SessionLocal, engine
from backend.infrastructure.db.models.orm_models import Base, UserORM
from backend.core.security import hash_password

TEST_USERS = [
    ("11111111-1111-1111-1111-111111111111", "analyst@fraud-platform.com", "ANALYST"),
    ("22222222-2222-2222-2222-222222222222", "manager@fraud-platform.com", "MANAGER"),
    ("33333333-3333-3333-3333-333333333333", "mlengineer@fraud-platform.com", "ML_ENGINEER"),
]

@pytest.fixture(scope="session", autouse=True)
def initialize_test_environment():
    """
    {
        func   : initialize_test_environment
        desc   : Khoi tao schema database SQLite cho phien test va don dep sau khi hoan tat
        input  : None
        output : None
        loop   : 0 loops
    }
    """
    init_db()
    db = SessionLocal()
    pw_hash = hash_password(TEST_PASSWORD)
    # { loop-1: seed 3 user test theo role }
    for uid, email, role in TEST_USERS:
        user = db.query(UserORM).filter_by(email=email).first()
        if user:
            user.hashed_password, user.role = pw_hash, role
        else:
            db.add(UserORM(id=uid, email=email, hashed_password=pw_hash, role=role))
    db.commit()
    db.close()
    yield
    # Giu nguyen hoac cleanup database neu can thiet


@pytest.fixture(scope="session")
def analyst_headers(initialize_test_environment):
    """Đăng nhập thật bằng user ANALYST đã seed và trả về header Bearer cho TestClient."""
    from fastapi.testclient import TestClient
    from backend.apps.api.main import app
    res = TestClient(app).post(
        "/api/v1/auth/login",
        json={"email": "analyst@fraud-platform.com", "password": TEST_PASSWORD},
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
