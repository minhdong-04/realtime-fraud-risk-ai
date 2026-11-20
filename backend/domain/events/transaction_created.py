"""
{
    module : transaction_created.py
    desc   : Sự kiện Domain phục vụ luồng xử lý giao dịch thời gian thực và chấm điểm rủi ro.
}
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from backend.domain.value_objects.risk_score import RiskScore

@dataclass(frozen=True)
class TransactionCreatedEvent:
    """
    {
        class  : TransactionCreatedEvent
        desc   : Domain Event phát ra khi một giao dịch mới được tiếp nhận thành công
        note   : Kích hoạt quy trình tính toán tập đặc trưng (features)
    }
    """
    transaction_id: str
    account_id: UUID
    amount: float
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class RiskScoredEvent:
    """
    {
        class  : RiskScoredEvent
        desc   : Domain Event phát ra khi quy trình chấm điểm rủi ro hoàn tất
        note   : Kích hoạt tạo fraud case nếu rủi ro mức HIGH
    }
    """
    transaction_id: str
    risk_score: RiskScore
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
