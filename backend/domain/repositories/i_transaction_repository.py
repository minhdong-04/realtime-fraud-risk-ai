"""
{
    module : i_transaction_repository.py
    desc   : Interface cho Repository quản lý Transaction (Domain Layer).
}
"""

from abc import ABC, abstractmethod
from uuid import UUID
from backend.domain.entities.transaction import Transaction

class ITransactionRepository(ABC):
    """
    {
        class  : ITransactionRepository
        desc   : Domain interface định nghĩa hợp đồng lưu trữ cho đối tượng Transaction
        note   : Cài đặt thực tế nằm ở tầng infrastructure
    }
    """

    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction:
        """
        {
            func   : save
            desc   : Lưu hoặc cập nhật thực thể transaction
            input  : transaction (Transaction) — thực thể cần lưu
            output : (Transaction) — thực thể đã được lưu
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: str) -> Transaction | None:
        """
        {
            func   : find_by_transaction_id
            desc   : Tìm kiếm transaction theo mã định danh bên ngoài
            input  : transaction_id (str) — mã giao dịch
            output : Transaction | None
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_by_account_id(self, account_id: UUID, limit: int = 50) -> list[Transaction]:
        """
        {
            func   : find_by_account_id
            desc   : Lấy lịch sử các giao dịch gần đây của tài khoản
            input  : account_id (UUID) — ID tài khoản
                     limit (int) — số lượng tối đa cần lấy
            output : list[Transaction]
            loop   : 0 loops
        }
        """
        ...
