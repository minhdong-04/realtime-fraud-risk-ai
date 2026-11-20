"""
{
    module : auth.py
    desc   : Router API Xác thực (Đăng nhập và cấp mã Token JWT).
}
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.security import create_access_token, verify_password
from backend.core.settings import settings
from backend.infrastructure.db.session import get_db
from backend.infrastructure.db.models.orm_models import UserORM

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    {
        func   : login
        desc   : Xác thực email/mật khẩu bằng bcrypt và trả về JWT chứa vai trò
        input  : payload (LoginRequest), db (Session)
        output : TokenResponse
        loop   : 0 loops
        throws : HTTPException 401 nếu đăng nhập sai
    }
    """
    user = db.query(UserORM).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")

    token = create_access_token(user.email, user.role, settings)
    return TokenResponse(access_token=token, role=user.role, email=user.email)
