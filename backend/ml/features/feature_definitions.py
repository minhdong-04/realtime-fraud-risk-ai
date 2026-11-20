"""
{
    module : feature_definitions.py
    desc   : Định nghĩa danh sách đặc trưng (Features): Nguồn sự thật duy nhất (Single Source of Truth) cho cả offline training và online serving.
}
"""

FEATURE_NAMES = [
    "txn_count_5m",
    "txn_count_1h",
    "amount_sum_1h",
    "unique_merchants_1h",
    "avg_amount_30d",
    "amount_ratio",
    "new_device_flag",
    "new_merchant_flag",
]

DEFAULT_FEATURE_VALUES = {
    "txn_count_5m": 0,
    "txn_count_1h": 0,
    "amount_sum_1h": 0.0,
    "unique_merchants_1h": 0,
    "avg_amount_30d": 100_000.0,
    "amount_ratio": 1.0,
    "new_device_flag": 0,
    "new_merchant_flag": 0,
}

FEATURE_LABELS = {
    "txn_count_5m": "Số lượng giao dịch trong cửa sổ 5 phút",
    "txn_count_1h": "Số lượng giao dịch trong cửa sổ 1 giờ",
    "amount_sum_1h": "Tổng số tiền giao dịch trong 1 giờ",
    "unique_merchants_1h": "Số merchant khác nhau đã ghé thăm trong 1 giờ",
    "avg_amount_30d": "Số tiền giao dịch trung bình 30 ngày của tài khoản",
    "amount_ratio": "Tỷ lệ số tiền hiện tại so với trung bình 30 ngày",
    "new_device_flag": "Cờ báo hiệu thiết bị chưa từng ghi nhận",
    "new_merchant_flag": "Cờ báo hiệu merchant mới đối với tài khoản",
}
