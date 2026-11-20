"""
{
    module : dependencies.py
    desc   : Tiêm phụ thuộc FastAPI (Dependency Injection) và phân quyền RBAC.
}
"""

from typing import Callable, Any
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.security import TokenValidationError, decode_access_token
from backend.core.settings import settings
from backend.infrastructure.db.session import get_db
from backend.infrastructure.db.models.orm_models import UserORM

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserORM:
    """
    {
        func   : get_current_user
        desc   : Xác thực JWT token từ Authorization Header và lấy thông tin người dùng tương ứng
        input  : credentials (HTTPAuthorizationCredentials | None), db (Session)
        output : UserORM
        loop   : 0 loops
        throws : HTTPException 401 nếu token thiếu, không hợp lệ hoặc hết hạn
    }
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Thiếu Authorization Token xác thực")

    try:
        claims = decode_access_token(credentials.credentials, settings)
    except TokenValidationError:
        raise HTTPException(status_code=401, detail="Không thể xác thực thông tin đăng nhập")

    user = db.query(UserORM).filter_by(email=claims.subject).first()
    if not user:
        raise HTTPException(status_code=401, detail="Không thể xác thực thông tin đăng nhập")
    return user

def roles_required(*allowed_roles: str):
    """
    {
        func   : roles_required
        desc   : Dependency FastAPI kiểm tra role người dùng (BR-11 RBAC) cho endpoint ghi dữ liệu
        input  : *allowed_roles (str) — các role được phép
        output : Callable dependency trả về UserORM
        loop   : 0 loops
        throws : HTTPException 403 nếu role không hợp lệ
    }
    """
    def checker(current_user: UserORM = Depends(get_current_user)) -> UserORM:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Vai trò {current_user.role} không có quyền gọi endpoint này")
        return current_user
    return checker

def require_role(*allowed_roles: str):
    """
    {
        func   : require_role
        desc   : Decorator kiểm tra phân quyền người dùng (Role-Based Access Control) trên endpoint
        input  : *allowed_roles (str) — danh sách các role được phép ("ANALYST", "MANAGER", "ML_ENGINEER")
        output : Hàm Decorator
        loop   : 0 loops
        throws : HTTPException 403 nếu người dùng không có vai trò phù hợp
    }
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, current_user: UserORM = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles and "ALL" not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Bị cấm truy cập: Vai trò {current_user.role} không có quyền gọi endpoint này",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
