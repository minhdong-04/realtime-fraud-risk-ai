"""
{
    module : postgres_outbox_repository.py
    desc   : Cài đặt thực tế của IOutboxRepository bằng SQLAlchemy / Postgres.
}
"""

from typing import Any
from sqlalchemy.orm import Session
from backend.domain.repositories.i_outbox_repository import IOutboxRepository
from backend.infrastructure.db.models.orm_models import AuditLogORM

class PostgresOutboxRepository(IOutboxRepository):
    """
    {
        class  : PostgresOutboxRepository
        desc   : Repository quản lý các sự kiện outbox bất đồng bộ
        pattern: Transactional Outbox Pattern
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def enqueue(self, event_type: str, aggregate_id: str, payload: dict[str, Any]) -> None:
        """
        {
            func   : enqueue
            desc   : Lưu sự kiện mới vào bảng outbox event trong cùng DB session
            input  : event_type (str), aggregate_id (str), payload (dict)
            output : None
            loop   : 0 loops
        }
        """
        orm = AuditLogORM(
            actor_id="system",
            actor_type="SYSTEM",
            action=event_type,
            resource_type="outbox",
            resource_id=aggregate_id,
            after_state=payload,
        )
        self._db.add(orm)

    def fetch_pending(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        {
            func   : fetch_pending
            desc   : Truy vấn các sự kiện outbox chưa xuất bản
            input  : limit (int)
            output : list[dict]
            loop   : 1 loop
        }
        """
        rows = self._db.query(AuditLogORM).filter_by(resource_type="outbox").limit(limit).all()
        # { loop-1: định dạng danh sách sự kiện outbox }
        return [{"id": r.id, "event_type": r.action, "payload": r.after_state} for r in rows]
