"""
{
    module : postgres_fraud_case_repository.py
    desc   : Implement IFraudCaseRepository su dung SQLAlchemy Session & SQLite/Postgres.
}
"""

from typing import Sequence
from uuid import UUID, uuid5, NAMESPACE_DNS
from datetime import datetime, timezone
import base64
import json
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.domain.entities.fraud_case import FraudCase, CaseStatus
from backend.domain.value_objects.risk_score import RiskScore, RiskLevel
from backend.domain.repositories.i_fraud_case_repository import IFraudCaseRepository
from backend.infrastructure.db.models.orm_models import FraudCaseORM

def _safe_uuid(val: str | None) -> UUID | None:
    """
    {
        func   : _safe_uuid
        desc   : Chuyen doi chuoi an toan sang UUID (fallback sang uuid5 neu khong phai hex 32)
        input  : val (str | None)
        output : UUID | None
        loop   : 0 loops
    }
    """
    if not val:
        return None
    try:
        return UUID(val)
    except Exception:
        return uuid5(NAMESPACE_DNS, str(val))

class PostgresFraudCaseRepository(IFraudCaseRepository):
    """
    {
        class  : PostgresFraudCaseRepository
        desc   : Repository quan ly ca rui ro gian lan voi ho tro Keyset Cursor Pagination O(1)
        pattern: Repository Pattern
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, case: FraudCase) -> FraudCase:
        orm = self._db.query(FraudCaseORM).filter_by(id=str(case.id)).first()
        if not orm:
            orm = FraudCaseORM(
                id=str(case.id),
                transaction_id=str(case.transaction_id),
                risk_score=case.risk_score.value,
                risk_level=case.risk_score.level.value,
                status=case.status.value,
                assigned_to=str(case.assigned_to) if case.assigned_to else None,
                created_at=case.created_at,
                closed_at=case.closed_at,
            )
            self._db.add(orm)
        else:
            orm.risk_score = case.risk_score.value
            orm.risk_level = case.risk_score.level.value
            orm.status = case.status.value
            orm.assigned_to = str(case.assigned_to) if case.assigned_to else None
            orm.closed_at = case.closed_at

        self._db.commit()
        return case

    def find_by_id(self, case_id: UUID) -> FraudCase | None:
        orm = self._db.query(FraudCaseORM).filter_by(id=str(case_id)).first()
        return self._to_domain(orm) if orm else None

    def find_by_transaction_id(self, transaction_id: UUID) -> FraudCase | None:
        orm = self._db.query(FraudCaseORM).filter_by(transaction_id=str(transaction_id)).first()
        return self._to_domain(orm) if orm else None

    def find_all(
        self,
        risk_level: RiskLevel | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[FraudCase]:
        query = self._db.query(FraudCaseORM)
        if risk_level:
            query = query.filter(FraudCaseORM.risk_level == risk_level.value)
        if status and status.upper() != "ALL":
            query = query.filter(FraudCaseORM.status == status.upper())
        rows = query.order_by(desc(FraudCaseORM.risk_score)).limit(limit).all()
        # { loop-1: format danh sach domain }
        return [self._to_domain(r) for r in rows]

    def find_by_status(self, status: CaseStatus) -> Sequence[FraudCase]:
        rows = self._db.query(FraudCaseORM).filter_by(status=status.value).all()
        # { loop-1: chuyen doi danh sach orm sang domain }
        return [self._to_domain(r) for r in rows]

    def find_paginated(
        self,
        risk_level: str | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int = 20,
    ) -> tuple[Sequence[FraudCase], str | None, bool, int]:
        """
        {
            func   : find_paginated
            desc   : Keyset Cursor Pagination O(1) dua tren created_at va id
            input  : risk_level (str), status (str), cursor (str), limit (int)
            output : tuple[danh_sach_ca, next_cursor, has_more, total_count]
            loop   : 1 loop — chuyen doi ket qua sang domain
        }
        """
        query = self._db.query(FraudCaseORM)
        if risk_level and risk_level.upper() != "ALL":
            query = query.filter(FraudCaseORM.risk_level == risk_level.upper())
        if status and status.upper() != "ALL":
            query = query.filter(FraudCaseORM.status == status.upper())

        total_count = query.count()

        if cursor:
            try:
                decoded = base64.b64decode(cursor).decode("utf-8")
                cursor_data = json.loads(decoded)
                cursor_ts = datetime.fromisoformat(cursor_data["created_at"])
                cursor_id = cursor_data["id"]

                query = query.filter(
                    (FraudCaseORM.created_at < cursor_ts)
                    | ((FraudCaseORM.created_at == cursor_ts) & (FraudCaseORM.id < cursor_id))
                )
            except Exception:
                pass

        query = query.order_by(desc(FraudCaseORM.created_at), desc(FraudCaseORM.id))
        rows = query.limit(limit + 1).all()

        has_more = len(rows) > limit
        result_rows = rows[:limit]

        next_cursor = None
        if has_more and result_rows:
            last_item = result_rows[-1]
            cursor_dict = {
                "created_at": last_item.created_at.isoformat(),
                "id": last_item.id,
            }
            next_cursor = base64.b64encode(json.dumps(cursor_dict).encode("utf-8")).decode("utf-8")

        # { loop-1: chuyen cac ban ghi thanh domain entities }
        return [self._to_domain(r) for r in result_rows], next_cursor, has_more, total_count

    def _to_domain(self, orm: FraudCaseORM) -> FraudCase:
        level = RiskLevel(orm.risk_level)
        risk_score = RiskScore(value=orm.risk_score, level=level)
        return FraudCase(
            id=_safe_uuid(orm.id) or UUID("00000000-0000-0000-0000-000000000000"),
            transaction_id=_safe_uuid(orm.transaction_id) or UUID("00000000-0000-0000-0000-000000000000"),
            risk_score=risk_score,
            status=CaseStatus(orm.status),
            assigned_to=_safe_uuid(orm.assigned_to),
            created_at=orm.created_at,
            closed_at=orm.closed_at,
        )
