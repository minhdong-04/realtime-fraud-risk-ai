"""
{
    module : fraud_case.py
    desc   : Thực thể Domain đại diện cho Fraud Case (ca rủi ro gian lận cần review).
}
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from backend.domain.value_objects.risk_score import RiskScore
from backend.domain.exceptions import CaseAlreadyClosedError

class CaseStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"

class AnalystDecision(str, Enum):
    LEGITIMATE = "LEGITIMATE"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    NEED_MORE_INFO = "NEED_MORE_INFO"

@dataclass
class FraudCase:
    """
    {
        class  : FraudCase
        desc   : Domain entity đại diện cho ca gian lận rủi ro cao cần Analyst xem xét
        rule   : Chỉ được tạo khi risk_level = HIGH (BR-04)
        note   : Các trường bất biến: id, transaction_id, created_at
    }
    """
    transaction_id: UUID
    risk_score: RiskScore
    id: UUID = field(default_factory=uuid4)
    status: CaseStatus = CaseStatus.OPEN
    assigned_to: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None

    def assign(self, analyst_id: UUID) -> None:
        """
        {
            func   : assign
            desc   : Phân công case cho analyst và chuyển trạng thái sang ASSIGNED
            input  : analyst_id (UUID) — ID của analyst được phân công
            output : None (thay đổi nội tại object)
            loop   : 0 loops
            throws : CaseAlreadyClosedError nếu case đã ở trạng thái CLOSED
        }
        """
        if self.status == CaseStatus.CLOSED:
            raise CaseAlreadyClosedError(f"Fraud case {self.id} đã được đóng trước đó")
        self.assigned_to = analyst_id
        self.status = CaseStatus.ASSIGNED

    def close(self) -> None:
        """
        {
            func   : close
            desc   : Đóng case sau khi analyst gửi quyết định kiểm tra
            input  : None
            output : None (thay đổi nội tại object)
            loop   : 0 loops
        }
        """
        self.status = CaseStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)
