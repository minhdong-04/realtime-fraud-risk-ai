"""
{
    module : velocity_features.py
    desc   : Tính toán các đặc trưng tốc độ giao dịch (velocity features) theo thời gian thực.
}
"""

from datetime import datetime, timedelta, timezone
from backend.domain.entities.transaction import Transaction
from backend.domain.exceptions import VelocityError

def _ensure_utc(dt: datetime) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def compute_txn_count_5m(
    history: list[Transaction],
    current_ts: datetime,
) -> int:
    """
    {
        func   : compute_txn_count_5m
        desc   : Đếm số lượng giao dịch trong khoảng thời gian 5 phút trước current_ts
        input  : history (list[Transaction]), current_ts (datetime)
        output : (int) — số lượng giao dịch
        loop   : 1 loop
        throws : VelocityError nếu current_ts là None
    }
    """
    if current_ts is None:
        raise VelocityError("current_ts không được là None")
    if not history:
        return 0

    ts = _ensure_utc(current_ts)
    cutoff = ts - timedelta(minutes=5)
    # { loop-1: lọc các giao dịch trong khoảng 5 phút }
    in_window = [t for t in history if cutoff <= _ensure_utc(t.created_at) < ts]
    return len(in_window)

def compute_txn_count_1h(
    history: list[Transaction],
    current_ts: datetime,
) -> int:
    """
    {
        func   : compute_txn_count_1h
        desc   : Đếm số lượng giao dịch trong khoảng thời gian 1 giờ trước current_ts
        input  : history (list[Transaction]), current_ts (datetime)
        output : (int) — số lượng giao dịch
        loop   : 1 loop
        throws : VelocityError nếu current_ts là None
    }
    """
    if current_ts is None:
        raise VelocityError("current_ts không được là None")
    if not history:
        return 0

    ts = _ensure_utc(current_ts)
    cutoff = ts - timedelta(hours=1)
    # { loop-2: lọc các giao dịch trong khoảng 1 giờ }
    in_window = [t for t in history if cutoff <= _ensure_utc(t.created_at) < ts]
    return len(in_window)

def compute_amount_sum_1h(
    history: list[Transaction],
    current_ts: datetime,
) -> float:
    """
    {
        func   : compute_amount_sum_1h
        desc   : Tính tổng số tiền giao dịch trong khoảng 1 giờ trước current_ts
        input  : history (list[Transaction]), current_ts (datetime)
        output : (float) — tổng số tiền giao dịch
        loop   : 1 loop
        throws : VelocityError nếu current_ts là None
    }
    """
    if current_ts is None:
        raise VelocityError("current_ts không được là None")
    if not history:
        return 0.0

    ts = _ensure_utc(current_ts)
    cutoff = ts - timedelta(hours=1)
    # { loop-3: tính tổng số tiền các giao dịch trong 1 giờ }
    return float(sum(t.amount for t in history if cutoff <= _ensure_utc(t.created_at) < ts))

def compute_unique_merchants_1h(
    history: list[Transaction],
    current_ts: datetime,
) -> int:
    """
    {
        func   : compute_unique_merchants_1h
        desc   : Đếm số merchant_id duy nhất được giao dịch trong 1 giờ trước current_ts
        input  : history (list[Transaction]), current_ts (datetime)
        output : (int) — số lượng merchant độc lập
        loop   : 1 loop
        throws : VelocityError nếu current_ts là None
    }
    """
    if current_ts is None:
        raise VelocityError("current_ts không được là None")
    if not history:
        return 0

    ts = _ensure_utc(current_ts)
    cutoff = ts - timedelta(hours=1)
    # { loop-4: trích xuất danh sách các merchant_id duy nhất trong 1 giờ }
    merchants = {t.merchant_id for t in history if cutoff <= _ensure_utc(t.created_at) < ts}
    return len(merchants)
