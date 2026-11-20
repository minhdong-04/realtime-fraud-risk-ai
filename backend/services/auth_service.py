"""
{
    module : auth_service.py
    desc   : Application Service xử lý xác thực và phân quyền người dùng.
}
"""

from sqlalchemy.orm import Session
from backend.infrastructure.db.models.orm_models import UserORM
from backend.core.security import verify_password, create_jwt_token

class AuthService:
    """
    {
        class  : AuthService
        desc   : Application service quản lý đăng nhập và cấp phát token JWT
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def authenticate_user(self, email: str, password: str) -> dict[str, str]:
        """
        {
            func   : authenticate_user
            desc   : Kiểm tra email/mật khẩu và trả về JWT token
            input  : email (str), password (str)
            output : dict — { access_token, role, email }
            loop   : 0 loops
            throws : ValueError nếu sai email hoặc mật khẩu
        }
        """
        user = self._db.query(UserORM).filter_by(email=email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Email hoặc mật khẩu không chính xác")

        token = create_jwt_token({"sub": user.email, "role": user.role, "user_id": user.id})
        return {
            "access_token": token,
            "role": user.role,
            "email": user.email,
        }
