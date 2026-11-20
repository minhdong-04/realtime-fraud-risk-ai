"""
{
    module : test_novelty_features.py
    desc   : Kiểm thử đơn vị cho các đặc trưng mới xuất hiện (UT-FE-20..24).
}
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from backend.domain.entities.transaction import Transaction, TransactionType, TransactionChannel
from backend.ml.features.novelty_features import compute_new_device_flag, compute_new_merchant_flag

def test_compute_new_device_flag_existing():
    # UT-FE-20: Thiết bị đã có trong lịch sử -> flag = 0
    dev_id = uuid4()
    history = [
        Transaction(
            transaction_id="t-1",
            account_id=uuid4(),
            merchant_id=uuid4(),
            device_id=dev_id,
            amount=100_000.0,
            currency="VND",
            transaction_type=TransactionType.PURCHASE,
            channel=TransactionChannel.WEB,
            created_at=datetime.now(timezone.utc),
        )
    ]
    assert compute_new_device_flag(dev_id, history) == 0

def test_compute_new_device_flag_new():
    # UT-FE-21: Thiết bị chưa có trong lịch sử -> flag = 1
    dev1, dev2 = uuid4(), uuid4()
    history = [
        Transaction(
            transaction_id="t-1",
            account_id=uuid4(),
            merchant_id=uuid4(),
            device_id=dev1,
            amount=100_000.0,
            currency="VND",
            transaction_type=TransactionType.PURCHASE,
            channel=TransactionChannel.WEB,
            created_at=datetime.now(timezone.utc),
        )
    ]
    assert compute_new_device_flag(dev2, history) == 1

def test_compute_new_merchant_flag_new():
    # UT-FE-22: Merchant chưa có trong lịch sử -> flag = 1
    m1, m2 = uuid4(), uuid4()
    history = [
        Transaction(
            transaction_id="t-1",
            account_id=uuid4(),
            merchant_id=m1,
            amount=100_000.0,
            currency="VND",
            transaction_type=TransactionType.PURCHASE,
            channel=TransactionChannel.WEB,
            created_at=datetime.now(timezone.utc),
        )
    ]
    assert compute_new_merchant_flag(m2, history) == 1
