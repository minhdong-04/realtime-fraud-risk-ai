"""
{
    module : i_outbox_repository.py
    desc   : Interface cho Repository quản lý Transactional Outbox (Domain Layer).
}
"""

from abc import ABC, abstractmethod
from typing import Any

class IOutboxRepository(ABC):
    """
    {
        class  : IOutboxRepository
        desc   : Interface định nghĩa việc lưu và truy xuất các sự kiện trong bảng Transactional Outbox
        pattern: Transactional Outbox Pattern
    }
    """

    @abstractmethod
    def enqueue(self, event_type: str, aggregate_id: str, payload: dict[str, Any]) -> None:
        """
        {
            func   : enqueue
            desc   : Thêm một sự kiện mới vào hàng đợi outbox cùng phiên làm việc DB transaction
            input  : event_type (str), aggregate_id (str), payload (dict)
            output : None
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def fetch_pending(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        {
            func   : fetch_pending
            desc   : Lấy danh sách các sự kiện chưa được xuất bản tới Kafka
            input  : limit (int)
            output : list[dict]
            loop   : 0 loops
        }
        """
        ...
