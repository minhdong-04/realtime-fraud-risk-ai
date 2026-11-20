"""
Unit tests for velocity features (UT-FE-01..07).
"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from backend.domain.entities.transaction import Transaction, TransactionType, TransactionChannel
from backend.domain.exceptions import VelocityError
from backend.ml.features.velocity_features import (
    compute_txn_count_5m, compute_txn_count_1h, compute_amount_sum_1h
)

@pytest.fixture
def base_time():
    return datetime(2026, 8, 11, 12, 0, 0)

@pytest.fixture
def sample_history(base_time):
    txns = []
    # { loop-1: generate 10 test transactions with varying timestamps }
    for i in range(10):
        ts = base_time - timedelta(minutes=i * 4)  # 0m, 4m, 8m, 12m, 16m, ...
        txns.append(
            Transaction(
                transaction_id=f"t-{i}",
                account_id=uuid4(),
                merchant_id=uuid4() if i < 3 else UUID("11111111-1111-1111-1111-111111111111"),
                amount=100_000.0 * (i + 1),
                currency="VND",
                transaction_type=TransactionType.PURCHASE,
                channel=TransactionChannel.WEB,
                created_at=ts,
            )
        )
    return txns

def test_compute_txn_count_5m(sample_history, base_time):
    count = compute_txn_count_5m(sample_history, base_time + timedelta(seconds=1))
    assert count == 2

def test_ut_fe_02_no_count_outside_5m_window(sample_history, base_time):
    """UT-FE-02: Không đếm các transaction nằm ngoài cửa sổ 5 phút"""
    future_time = base_time + timedelta(minutes=60)
    count = compute_txn_count_5m(sample_history, future_time)
    assert count == 0

def test_ut_fe_03_boundary_5m_inclusive(sample_history, base_time):
    """UT-FE-03: Boundary check tại đúng mốc 5 phút"""
    exact_5m = base_time + timedelta(minutes=5)
    count = compute_txn_count_5m(sample_history, exact_5m)
    assert count >= 1

def test_ut_fe_06_empty_history_returns_zero(base_time):
    """UT-FE-06: Lịch sử rỗng [] trả về 0"""
    count = compute_txn_count_5m([], base_time)
    assert count == 0

def test_compute_txn_count_1h(sample_history, base_time):
    count = compute_txn_count_1h(sample_history, base_time + timedelta(seconds=1))
    assert count == 10

def test_compute_amount_sum_1h(sample_history, base_time):
    total = compute_amount_sum_1h(sample_history, base_time + timedelta(seconds=1))
    assert total == sum(100_000.0 * (i + 1) for i in range(10))

def test_compute_txn_count_5m_none_ts(sample_history):
    with pytest.raises(VelocityError):
        compute_txn_count_5m(sample_history, None)
