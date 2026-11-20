"""
{
    module : risk_threshold_policy.py
    desc   : Chính sách ngưỡng rủi ro đóng gói quy tắc nghiệp vụ BR-02 và BR-03.
}
"""

from backend.domain.value_objects.risk_score import RiskLevel

class RiskThresholdPolicy:
    """
    {
        class  : RiskThresholdPolicy
        desc   : Policy object đóng gói logic phân loại mức độ rủi ro và quy tắc override nghiệp vụ
        pattern: Policy Object Pattern
        rule   : BR-02 (LOW < 30, MEDIUM 30-69, HIGH >= 70), BR-03 (amount > limit VÀ new_device -> force HIGH)
    }
    """

    def __init__(
        self,
        high_threshold: int = 70,
        medium_threshold: int = 30,
        amount_override_limit: float = 10_000_000.0,
    ) -> None:
        self._high = high_threshold
        self._medium = medium_threshold
        self._amount_limit = amount_override_limit

    def determine_level(
        self,
        score: int,
        amount: float,
        is_new_device: bool,
    ) -> RiskLevel:
        """
        {
            func   : determine_level
            desc   : Xác định RiskLevel từ điểm số với quy tắc nghiệp vụ override BR-03
            input  : score (int) — điểm rủi ro 0-100 từ risk engine
                     amount (float) — số tiền giao dịch
                     is_new_device (bool) — cờ báo thiết bị mới chưa từng dùng
            output : (RiskLevel) — LOW | MEDIUM | HIGH
            loop   : 0 loops
            note   : BR-03: amount > limit VÀ is_new_device -> force HIGH rủi ro dù score thấp
        }
        """
        # { rule BR-03: override nghiệp vụ cho giao dịch giá trị cao trên thiết bị mới }
        if amount > self._amount_limit and is_new_device:
            return RiskLevel.HIGH

        if score >= self._high:
            return RiskLevel.HIGH
        if score >= self._medium:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
