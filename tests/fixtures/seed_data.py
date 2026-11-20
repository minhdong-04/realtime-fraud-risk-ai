"""
{
    module : seed_data.py
    desc   : Fixtures du lieu mau khoi tao phuc vu cac bai kiem thu unit/integration.
}
"""

from uuid import uuid4
from datetime import datetime, timezone

def get_sample_transaction_dict() -> dict:
    """Tra ve dictionary du lieu giao dich mau hop le"""
    return {
        "transaction_id": f"TXN-FIXTURE-{uuid4()}",
        "account_id": str(uuid4()),
        "merchant_id": str(uuid4()),
        "device_id": "device-fixture-001",
        "amount": 250000.0,
        "currency": "VND",
        "transaction_type": "PURCHASE",
        "channel": "WEB",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

def get_sample_feature_vector() -> dict:
    """Tra ve dictionary 8 dac trung thoi gian thuc chuan hoa"""
    return {
        "txn_count_5m": 2,
        "txn_count_1h": 5,
        "amount_sum_1h": 750000.0,
        "unique_merchants_1h": 2,
        "avg_amount_30d": 300000.0,
        "amount_ratio": 0.83,
        "new_device_flag": 0,
        "new_merchant_flag": 0,
    }
