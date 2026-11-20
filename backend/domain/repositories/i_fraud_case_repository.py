"""
{
    module : i_fraud_case_repository.py
    desc   : Interface cho Repository quản lý Fraud Case (Domain Layer).
}
"""

from abc import ABC, abstractmethod
from uuid import UUID
from backend.domain.entities.fraud_case import FraudCase
from backend.domain.value_objects.risk_score import RiskLevel

class IFraudCaseRepository(ABC):
    """
    {
        class  : IFraudCaseRepository
        desc   : Domain interface định nghĩa hợp đồng lưu trữ Fraud Case
        note   : Cài đặt thực tế nằm ở tầng infrastructure
    }
    """

    @abstractmethod
    def save(self, case: FraudCase) -> FraudCase:
        """
        {
            func   : save
            desc   : Lưu hoặc cập nhật ca gian lận rủi ro
            input  : case (FraudCase) — thực thể cần lưu
            output : FraudCase — thực thể đã lưu
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_by_id(self, case_id: UUID) -> FraudCase | None:
        """
        {
            func   : find_by_id
            desc   : Tìm ca gian lận theo ID khóa chính
            input  : case_id (UUID)
            output : FraudCase | None
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: UUID) -> FraudCase | None:
        """
        {
            func   : find_by_transaction_id
            desc   : Tìm ca gian lận theo ID giao dịch
            input  : transaction_id (UUID)
            output : FraudCase | None
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_all(
        self,
        risk_level: RiskLevel | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[FraudCase]:
        """
        {
            func   : find_all
            desc   : Lấy danh sách ca gian lận theo bộ lọc, sắp xếp theo risk_score giảm dần
            input  : risk_level (RiskLevel | None) — bộ lọc mức độ rủi ro
                     status (str | None) — bộ lọc trạng thái
                     limit (int) — số lượng tối đa
            output : list[FraudCase]
            loop   : 0 loops
        }
        """
        ...
