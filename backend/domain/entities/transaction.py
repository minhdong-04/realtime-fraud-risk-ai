"""
{
    module : transaction.py
    desc   : Thực thể Domain đại diện cho Giao dịch thanh toán.
}
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum

class TransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    TRANSFER = "TRANSFER"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"

class TransactionChannel(str, Enum):
    WEB = "WEB"
    MOBILE = "MOBILE"
    POS = "POS"
    API = "API"

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SCORED = "SCORED"
    SCORING_FAILED = "SCORING_FAILED"
    PROCESSED = "PROCESSED"

@dataclass
class Transaction:
    """
    {
        class  : Transaction
        desc   : Domain entity đại diện cho một giao dịch thanh toán cần chấm điểm rủi ro
        note   : Các trường bất biến: id, transaction_id, created_at
    }
    """
    transaction_id: str
    account_id: UUID
    merchant_id: UUID
    amount: float
    currency: str
    transaction_type: TransactionType
    channel: TransactionChannel
    device_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scored_at: datetime | None = None

    def mark_scored(self, scored_time: datetime | None = None) -> None:
        """
        {
            func   : mark_scored
            desc   : Cập nhật trạng thái giao dịch sang SCORED cùng thời điểm chấm điểm
            input  : scored_time (datetime | None) — thời điểm chấm điểm xong
            output : None (thay đổi nội tại object)
            loop   : 0 loops
        }
        """
        self.status = TransactionStatus.SCORED
        self.scored_at = scored_time or datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """
        {
            func   : mark_failed
            desc   : Cập nhật trạng thái giao dịch sang SCORING_FAILED khi chấm điểm lỗi
            input  : None
            output : None (thay đổi nội tại object)
            loop   : 0 loops
        }
        """
        self.status = TransactionStatus.SCORING_FAILED
