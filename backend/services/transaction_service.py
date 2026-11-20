"""
{
    module : transaction_service.py
    desc   : Application Service quản lý quy trình tiếp nhận và truy vấn giao dịch.
}
"""

from uuid import UUID
from backend.domain.entities.transaction import Transaction, TransactionType, TransactionChannel
from backend.domain.repositories.i_transaction_repository import ITransactionRepository

class TransactionService:
    """
    {
        class  : TransactionService
        desc   : Application service điều phối luồng tạo mới và truy vấn giao dịch
    }
    """

    def __init__(self, repo: ITransactionRepository) -> None:
        self._repo = repo

    def submit_transaction(
        self,
        transaction_id: str,
        account_id: UUID,
        merchant_id: UUID,
        amount: float,
        currency: str = "VND",
        transaction_type: TransactionType = TransactionType.PURCHASE,
        channel: TransactionChannel = TransactionChannel.WEB,
        device_id: UUID | None = None,
    ) -> Transaction:
        """
        {
            func   : submit_transaction
            desc   : Tiếp nhận giao dịch mới và kiểm tra quy tắc trùng lặp Idempotency (BR-05)
            input  : transaction_id (str), account_id (UUID), merchant_id (UUID), amount (float), ...
            output : Transaction
            loop   : 0 loops
            throws : ValueError nếu amount <= 0 hoặc transaction_id đã tồn tại
        }
        """
        if amount <= 0:
            raise ValueError("Số tiền giao dịch phải lớn hơn 0")

        existing = self._repo.find_by_transaction_id(transaction_id)
        if existing:
            raise ValueError(f"Mã giao dịch bị trùng lặp (Idempotency): {transaction_id}")

        txn = Transaction(
            transaction_id=transaction_id,
            account_id=account_id,
            merchant_id=merchant_id,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            channel=channel,
            device_id=device_id,
        )
        return self._repo.save(txn)

    def get_by_transaction_id(self, transaction_id: str) -> Transaction | None:
        """
        {
            func   : get_by_transaction_id
            desc   : Lấy chi tiết giao dịch theo mã transaction_id
            input  : transaction_id (str)
            output : Transaction | None
            loop   : 0 loops
        }
        """
        return self._repo.find_by_transaction_id(transaction_id)

    def get_account_history(self, account_id: UUID, limit: int = 50) -> list[Transaction]:
        """
        {
            func   : get_account_history
            desc   : Lấy lịch sử giao dịch cũ của tài khoản (US-09)
            input  : account_id (UUID), limit (int)
            output : list[Transaction]
            loop   : 0 loops
        }
        """
        return self._repo.find_by_account_id(account_id, limit=limit)
