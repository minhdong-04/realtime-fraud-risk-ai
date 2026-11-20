"""
{
    module : novelty_features.py
    desc   : Tính toán các đặc trưng mới xuất hiện (novelty features) như thiết bị mới hoặc merchant mới.
}
"""

from uuid import UUID
from backend.domain.entities.transaction import Transaction

def compute_new_device_flag(
    device_id: UUID | None,
    history: list[Transaction],
) -> int:
    """
    {
        func   : compute_new_device_flag
        desc   : Kiểm tra thiết bị hiện tại có phải thiết bị mới (chưa từng dùng trong lịch sử)
        input  : device_id (UUID | None) — ID thiết bị giao dịch hiện tại
                 history (list[Transaction]) — lịch sử giao dịch của tài khoản
        output : (int) — 1 nếu thiết bị mới/không xác định, 0 nếu đã dùng trước đó
        loop   : 1 loop — kiểm tra sự tồn tại của device_id trong lịch sử
    }
    """
    if device_id is None:
        return 1
    if not history:
        return 1

    # { loop-1: duyệt lịch sử xem thiết bị đã từng được sử dụng chưa }
    seen = any(t.device_id == device_id for t in history if t.device_id is not None)
    return 0 if seen else 1

def compute_new_merchant_flag(
    merchant_id: UUID,
    history: list[Transaction],
) -> int:
    """
    {
        func   : compute_new_merchant_flag
        desc   : Kiểm tra merchant hiện tại có phải merchant mới đối với tài khoản
        input  : merchant_id (UUID) — ID merchant hiện tại
                 history (list[Transaction]) — lịch sử giao dịch của tài khoản
        output : (int) — 1 nếu merchant mới, 0 nếu đã ghé thăm trước đây
        loop   : 1 loop — kiểm tra sự tồn tại của merchant_id trong lịch sử
    }
    """
    if not history:
        return 1

    # { loop-2: duyệt lịch sử xem merchant đã từng thực hiện giao dịch chưa }
    seen = any(t.merchant_id == merchant_id for t in history)
    return 0 if seen else 1
