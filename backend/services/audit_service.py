"""
{
    module : audit_service.py
    desc   : Application Service cho quản lý và truy vấn nhật ký kiểm vết Audit Trail.
}
"""

from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from backend.infrastructure.db.models.orm_models import AuditLogORM

class AuditService:
    """
    {
        class  : AuditService
        desc   : Application service quản lý dữ liệu nhật ký kiểm vết
        rule   : Các bản ghi nhật ký kiểm vết là bất biến (BR-10)
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_logs_by_resource(self, resource_id: UUID) -> list[dict[str, Any]]:
        """
        {
            func   : get_logs_by_resource
            desc   : Truy vấn lịch sử nhật ký kiểm vết theo ID tài nguyên
            input  : resource_id (UUID)
            output : list[dict] — danh sách các bản ghi nhật ký
            loop   : 1 loop — định dạng bản ghi ORM thành các dictionary JSON
        }
        """
        rows = (
            self._db.query(AuditLogORM)
            .filter_by(resource_id=str(resource_id))
            .order_by(AuditLogORM.created_at.desc())
            .all()
        )
        # { loop-1: định dạng từng bản ghi audit log ORM sang định dạng dictionary }
        return [
            {
                "id": row.id,
                "actor_id": row.actor_id,
                "actor_type": row.actor_type,
                "action": row.action,
                "resource_type": row.resource_type,
                "resource_id": row.resource_id,
                "before_state": row.before_state,
                "after_state": row.after_state,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
