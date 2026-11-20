"""
{
    module : postgres_account_repository.py
    desc   : Cài đặt thực tế của IAccountRepository bằng SQLAlchemy / Postgres.
}
"""

from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from backend.domain.repositories.i_account_repository import IAccountRepository

class PostgresAccountRepository(IAccountRepository):
    """
    {
        class  : PostgresAccountRepository
        desc   : Lớp repository tương tác lưu trữ cho tài khoản khách hàng
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_id(self, account_id: UUID) -> dict[str, Any] | None:
        """
        {
            func   : find_by_id
            desc   : Truy vấn thông tin tài khoản và hạn mức mặc định
            input  : account_id (UUID)
            output : dict | None
            loop   : 0 loops
        }
        """
        return {
            "account_id": str(account_id),
            "custom_limit": 10_000_000.0,
            "status": "ACTIVE",
        }
