"""
{
    module : risk_score.py
    desc   : Value Object RiskScore và Enum RiskLevel.
}
"""

from enum import Enum
from dataclasses import dataclass

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass(frozen=True)
class RiskScore:
    """
    {
        class  : RiskScore
        desc   : Value Object bất biến đại diện cho điểm rủi ro (0-100) và mức độ rủi ro tương ứng
        rule   : Điểm rủi ro phải là số nguyên trong khoảng từ 0 đến 100 (BR-02)
    }
    """
    value: int
    level: RiskLevel

    def __post_init__(self) -> None:
        """
        {
            func   : __post_init__
            desc   : Kiểm tra tính hợp lệ của giá trị điểm rủi ro [0, 100]
            input  : self
            output : None
            loop   : 0 loops
            throws : ValueError nếu giá trị điểm rủi ro nằm ngoài khoảng [0, 100]
        }
        """
        if not (0 <= self.value <= 100):
            raise ValueError(f"Giá trị risk score {self.value} nằm ngoài khoảng hợp lệ [0, 100]")
