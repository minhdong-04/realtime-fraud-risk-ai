"""
{
    module : feature_consumer.py
    desc   : Worker Consumer lắng nghe transaction.created để tính toán đặc trưng online.
}
"""

from datetime import datetime, timezone
from typing import Any
from backend.ml.features.behavioural_features import compute_amount_ratio, compute_avg_amount_30d
from backend.ml.features.novelty_features import compute_new_device_flag, compute_new_merchant_flag
from backend.ml.features.velocity_features import (
    compute_amount_sum_1h,
    compute_txn_count_1h,
    compute_txn_count_5m,
    compute_unique_merchants_1h,
)


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
            desc   : Xử lý sự kiện transaction.created và tính vector đặc trưng online
            input  : event_data (dict)
            output : dict[str, float] — đặc trưng tính toán được
            loop   : 0 loops
        }
        """
        history = event_data.get("history") or []
        now = datetime.now(timezone.utc)
        amount = float(event_data.get("amount", 0.0))
        avg_30d = compute_avg_amount_30d(history)
        return {
            "txn_count_5m": float(compute_txn_count_5m(history, now)),
            "txn_count_1h": float(compute_txn_count_1h(history, now)),
            "amount_sum_1h": compute_amount_sum_1h(history, now),
            "unique_merchants_1h": float(compute_unique_merchants_1h(history, now)),
            "avg_amount_30d": avg_30d,
            "amount_ratio": compute_amount_ratio(amount, avg_30d),
            "new_device_flag": float(compute_new_device_flag(event_data.get("device_id"), history)),
            "new_merchant_flag": float(compute_new_merchant_flag(event_data.get("merchant_id"), history)),
        }
