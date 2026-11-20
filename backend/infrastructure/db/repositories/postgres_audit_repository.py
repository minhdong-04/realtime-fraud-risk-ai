"""
{
    module : postgres_audit_repository.py
    desc   : Cài đặt thực tế của IAuditRepository bằng SQLAlchemy / Postgres (Nhật ký audit bất biến).
}
"""

from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from backend.domain.repositories.i_audit_repository import IAuditRepository
from backend.infrastructure.db.models.orm_models import AuditLogORM

class PostgresAuditRepository(IAuditRepository):
    """
    {
        class  : PostgresAuditRepository
        desc   : Lớp Repository quản lý lưu trữ nhật ký kiểm vết bất biến trong database
        rule   : Các bản ghi audit không thể sửa hoặc xóa (BR-10, NFR-SEC-07)
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def log(
        self,
        actor_id: UUID,
        actor_type: str,
        action: str,
        resource_type: str,
        resource_id: UUID,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
    ) -> None:
        """
        {
            func   : log
            desc   : Thêm một bản ghi nhật ký audit trail mới vào bảng cơ sở dữ liệu
            input  : actor_id (UUID), actor_type (str), action (str), resource_type (str), resource_id (UUID), before_state, after_state
            output : None
            loop   : 0 loops
        }
        """
        orm = AuditLogORM(
            actor_id=str(actor_id),
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            before_state=before_state,
            after_state=after_state,
        )
        self._db.add(orm)
        self._db.commit()
