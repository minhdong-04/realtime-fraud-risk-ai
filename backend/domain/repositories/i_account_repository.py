"""
{
    module : i_account_repository.py
    desc   : Interface cho Repository quản lý thông tin Account (Domain Layer).
}
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Any

class IAccountRepository(ABC):
    """
    {
        class  : IAccountRepository
        desc   : Interface định nghĩa hợp đồng truy vấn thông tin tài khoản và hạn mức
    }
    """

    @abstractmethod
    def find_by_id(self, account_id: UUID) -> dict[str, Any] | None:
        """
        {
            func   : find_by_id
            desc   : Tìm thông tin tài khoản theo ID
            input  : account_id (UUID)
            output : dict | None
            loop   : 0 loops
        }
        """
        ...
