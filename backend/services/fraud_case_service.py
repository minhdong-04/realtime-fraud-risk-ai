"""
{
    module : fraud_case_service.py
    desc   : Application Service quản lý danh sách Fraud Case và quy trình kiểm tra của Analyst.
}
"""

from uuid import UUID
from typing import Any
from sqlalchemy.orm import Session

from backend.domain.entities.fraud_case import FraudCase, AnalystDecision, CaseStatus
from backend.domain.repositories.i_fraud_case_repository import IFraudCaseRepository
from backend.domain.value_objects.risk_score import RiskScore, RiskLevel
from backend.domain.exceptions import CaseAlreadyClosedError
from backend.infrastructure.db.models.orm_models import AnalystReviewORM, FraudLabelORM, AuditLogORM, FraudCaseORM

class FraudCaseService:
    """
    {
        class  : FraudCaseService
        desc   : Application service xử lý hàng chờ review, phân công ca và gửi kết quả của Analyst
    }
    """

    def __init__(self, db: Session, repo: IFraudCaseRepository | None = None) -> None:
        self._db = db
        if repo is None:
            from backend.infrastructure.db.repositories.postgres_fraud_case_repository import PostgresFraudCaseRepository
            self._repo = PostgresFraudCaseRepository(db)
        else:
            self._repo = repo

    def get_review_queue(self, level: str | None = None, status: str | None = None) -> list[FraudCase]:
        """
        {
            func   : get_review_queue
            desc   : Lấy hàng chờ ca gian lận cần review sắp xếp theo risk_score giảm dần (US-01)
            input  : level (str | None), status (str | None)
            output : list[FraudCase]
            loop   : 0 loops
        }
        """
        target_status = status if status and status != "ALL" else "OPEN"
        return self._repo.find_all(status=target_status, limit=100)

    def assign_case(self, case_id: UUID, analyst_id: UUID) -> None:
        """Phân công case cho analyst"""
        case = self._repo.find_by_id(case_id)
        if not case:
            raise ValueError(f"Không tìm thấy fraud case {case_id}")
        case.assign(analyst_id)
        self._repo.save(case)

    def create_case_if_high_risk(self, transaction_id: str, risk_level: str, risk_score: int) -> FraudCaseORM | None:
        """Tự động mở Fraud Case khi rủi ro HIGH (BR-04)"""
        if risk_level == "HIGH":
            case_orm = FraudCaseORM(
                transaction_id=transaction_id,
                risk_level="HIGH",
                risk_score=risk_score,
                status="OPEN",
            )
            self._db.add(case_orm)
            self._db.commit()
            return case_orm
        return None

    def submit_review(
        self,
        case_id: UUID,
        analyst_id: UUID,
        decision: AnalystDecision,
        reason: str,
    ) -> None:
        """
        {
            func   : submit_review
            desc   : Gửi kết quả đánh giá của Analyst cho một ca rủi ro (US-03)
            input  : case_id (UUID), analyst_id (UUID), decision (AnalystDecision), reason (str)
            output : None
            loop   : 0 loops
            throws : ValueError nếu reason ngắn hơn 10 ký tự, CaseAlreadyClosedError nếu ca đã closed
        }
        """
        if not reason or len(reason.strip()) < 10:
            raise ValueError("Lý do giải trình là bắt buộc và phải có ít nhất 10 ký tự")

        case = self._repo.find_by_id(case_id)
        if not case:
            raise ValueError(f"Không tìm thấy fraud case {case_id}")

        if case.status == CaseStatus.CLOSED:
            raise CaseAlreadyClosedError(f"Fraud case {case_id} đã được đóng trước đó")

        # 1. Cập nhật Thực thể Domain
        before_state = {"status": case.status.value, "assigned_to": str(case.assigned_to) if case.assigned_to else None}
        case.assign(analyst_id)
        case.close()
        self._repo.save(case)

        # 2. Lưu bản ghi Analyst Review
        review_orm = AnalystReviewORM(
            case_id=str(case.id),
            analyst_id=str(analyst_id),
            decision=decision.value,
            reason=reason.strip(),
        )
        self._db.add(review_orm)

        # 3. Lưu nhãn Fraud Label phản hồi cho retraining
        if decision == AnalystDecision.CONFIRMED_FRAUD:
            label_orm = FraudLabelORM(
                transaction_id=str(case.transaction_id),
                label=1,
                source="ANALYST_REVIEW",
            )
            self._db.add(label_orm)
        elif decision == AnalystDecision.LEGITIMATE:
            label_orm = FraudLabelORM(
                transaction_id=str(case.transaction_id),
                label=0,
                source="ANALYST_REVIEW",
            )
            self._db.add(label_orm)

        # 4. Ghi bản ghi Audit Trail bất biến
        audit_orm = AuditLogORM(
            actor_id=str(analyst_id),
            actor_type="USER",
            action="SUBMIT_REVIEW",
            resource_type="fraud_case",
            resource_id=str(case.id),
            before_state=before_state,
            after_state={"status": case.status.value, "decision": decision.value, "reason": reason.strip()},
        )
        self._db.add(audit_orm)
        self._db.commit()
