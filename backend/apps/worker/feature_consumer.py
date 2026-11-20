"""
{
    module : feature_consumer.py
    desc   : Worker Consumer lắng nghe transaction.created để tính toán đặc trưng online.
}
"""

from typing import Any
from backend.ml.features.online_features import compute_online_features

class FeatureConsumer:
    """
    {
        class  : FeatureConsumer
        desc   : Worker lắng nghe sự kiện tạo giao dịch và tính toán vector đặc trưng real-time
    }
    """

    def process_event(self, event_data: dict[str, Any]) -> dict[str, float]:
        """
        {
            func   : process_event
            desc   : Xử lý sự kiện transaction.created và lưu đặc trưng vào Redis
            input  : event_data (dict)
            output : dict[str, float] — đặc trưng tính toán được
            loop   : 0 loops
        }
        """
        features = compute_online_features(event_data, history=[])
        return features
