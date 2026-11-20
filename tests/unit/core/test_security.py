"""
{
    module : test_security.py
    desc   : Kiểm thử bảo mật mã hóa JWT và phân quyền RBAC.
}
"""

import pytest
import jwt
from backend.apps.api.dependencies import SECRET_KEY, ALGORITHM

def test_jwt_token_encode_decode():
    # Kiểm thử tạo và giải mã JWT token thành công
    payload = {"sub": "analyst@fraud-platform.com", "role": "ANALYST"}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "analyst@fraud-platform.com"
    assert decoded["role"] == "ANALYST"
