"""
{
    module : account_limit_policy.py
    desc   : Chính sách hạn mức tài khoản khách hàng (Account Limit Policy).
}
"""

class AccountLimitPolicy:
    """
    {
        class  : AccountLimitPolicy
        desc   : Đóng gói logic kiểm tra hạn mức tùy chỉnh theo tài khoản khách hàng
    }
    """

    def __init__(self, default_limit: float = 10_000_000.0) -> None:
        self._default_limit = default_limit

    def is_exceeded(self, amount: float, custom_limit: float | None = None) -> bool:
        """
        {
            func   : is_exceeded
            desc   : Kiểm tra xem số tiền giao dịch có vượt hạn mức của tài khoản hay không
            input  : amount (float), custom_limit (float | None)
            output : (bool)
            loop   : 0 loops
        }
        """
        limit = custom_limit if custom_limit is not None else self._default_limit
        return amount > limit
