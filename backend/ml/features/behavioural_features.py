"""
{
    module : behavioural_features.py
    desc   : Tính toán các đặc trưng hành vi (behavioural features) của tài khoản.
}
"""

from backend.domain.entities.transaction import Transaction

def compute_avg_amount_30d(
    history: list[Transaction],
    default_avg: float = 100_000.0,
) -> float:
    """
    {
        func   : compute_avg_amount_30d
        desc   : Tính số tiền giao dịch trung bình trong lịch sử của tài khoản
        input  : history (list[Transaction]) — lịch sử giao dịch của tài khoản
                 default_avg (float) — giá trị mặc định khi lịch sử trống
        output : (float) — số tiền trung bình
        loop   : 1 loop — cộng tổng số tiền các giao dịch
    }
    """
    if not history:
        return default_avg

    # { loop-1: tính tổng số tiền giao dịch trong lịch sử }
    total_amount = sum(t.amount for t in history)
    return float(total_amount / len(history))

def compute_amount_ratio(
    current_amount: float,
    avg_amount: float,
    epsilon: float = 1.0,
) -> float:
    """
    {
        func   : compute_amount_ratio
        desc   : Tính tỷ lệ số tiền giao dịch hiện tại so với trung bình lịch sử (chống chia cho 0)
        input  : current_amount (float) — số tiền giao dịch hiện tại
                 avg_amount (float) — số tiền trung bình lịch sử
                 epsilon (float) — số cộng an toàn cho mẫu số khi avg_amount = 0
        output : (float) — tỷ lệ số tiền
        loop   : 0 loops
    }
    """
    safe_denom = avg_amount if avg_amount > 0 else epsilon
    return float(current_amount / safe_denom)
