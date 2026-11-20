"""
{
    module : model_version.py
    desc   : Thực thể Domain đại diện cho phiên bản mô hình Machine Learning.
}
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum

class ModelStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"

@dataclass
class ModelVersion:
    """
    {
        class  : ModelVersion
        desc   : Domain entity đại diện cho một phiên bản mô hình ML được phát hành
        note   : Dùng cho MLOps registry, shadow deployment và chuyển đổi phiên bản model
    }
    """
    name: str
    version: str
    pr_auc: float
    recall: float
    precision: float
    f1_score: float
    brier_score: float
    expected_cost: float
    id: UUID = field(default_factory=uuid4)
    status: ModelStatus = ModelStatus.CANDIDATE
    is_shadow: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    promoted_at: datetime | None = None

    def promote(self) -> None:
        """
        {
            func   : promote
            desc   : Thăng cấp phiên bản mô hình ứng viên sang trạng thái PRODUCTION
            input  : None
            output : None (thay đổi nội tại object)
            loop   : 0 loops
        }
        """
        self.status = ModelStatus.PRODUCTION
        self.promoted_at = datetime.now(timezone.utc)

    def retire(self) -> None:
        """
        {
            func   : retire
            desc   : Chuyển phiên bản mô hình đang chạy sản xuất sang trạng thái RETIRED
            input  : None
            output : None (thay đổi nội tại object)
            loop   : 0 loops
        }
        """
        self.status = ModelStatus.RETIRED
