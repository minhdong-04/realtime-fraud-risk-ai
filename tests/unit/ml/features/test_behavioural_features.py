"""
{
    module : test_behavioural_features.py
    desc   : Kiểm thử đơn vị cho các đặc trưng hành vi (UT-FE-10..14).
}
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from backend.domain.entities.transaction import Transaction, TransactionType, TransactionChannel
from backend.ml.features.behavioural_features import compute_avg_amount_30d, compute_amount_ratio

@pytest.fixture
def sample_history():
    now = datetime.now(timezone.utc)
    return [
        Transaction(
            transaction_id=f"t-{i}",
            account_id=uuid4(),
            merchant_id=uuid4(),
            amount=amt,
            currency="VND",
            transaction_type=TransactionType.PURCHASE,
            channel=TransactionChannel.WEB,
            created_at=now,
        )
        for i, amt in enumerate([100_000.0, 200_000.0, 300_000.0])
    ]

def test_compute_avg_amount_30d(sample_history):
    # UT-FE-10: Tính trung bình cộng chính xác (100k + 200k + 300k) / 3 = 200k
    avg = compute_avg_amount_30d(sample_history)
    assert avg == 200_000.0

def test_compute_avg_amount_30d_empty():
    # UT-FE-11: Lịch sử trống trả về giá trị mặc định
    avg = compute_avg_amount_30d([])
    assert avg == 100_000.0

def test_compute_amount_ratio():
    # UT-FE-12: Tính tỷ lệ giao dịch so với trung bình
    ratio = compute_amount_ratio(500_000.0, 250_000.0)
    assert ratio == 2.0

def test_compute_amount_ratio_zero_avg():
    # UT-FE-13: Chống lỗi chia cho 0 khi trung bình = 0
    ratio = compute_amount_ratio(500_000.0, 0.0)
    assert ratio > 0.0
