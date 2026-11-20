"""
{
    module : i_audit_repository.py
    desc   : Interface cho Repository nhật ký kiểm vết bất biến (Audit Log).
}
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

class IAuditRepository(ABC):
    """
    {
        class  : IAuditRepository
        desc   : Interface định nghĩa việc ghi nhật ký audit trail bất biến
        rule   : Audit log là bất biến, không được sửa hoặc xóa (BR-10, NFR-SEC-07)
    }
    """

    @abstractmethod
    def log(
        self,
        actor_id: UUID,
        actor_type: str,
        action: str,
        resource_type: str,
        resource_id: UUID,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
    ) -> None:
        """
        {
            func   : log
            desc   : Ghi một bản ghi nhật ký audit trail mới
            input  : actor_id (UUID) — ID của người dùng hoặc hệ thống thực hiện
                     actor_type (str) — USER | SYSTEM | ML_ENGINE
                     action (str) — tên hành động (ví dụ: SUBMIT_REVIEW, PROMOTE_MODEL)
                     resource_type (str) — tên loại tài nguyên chịu tác động
                     resource_id (UUID) — ID của tài nguyên
                     before_state (dict | None) — trạng thái trước khi đổi
                     after_state (dict | None) — trạng thái sau khi đổi
            output : None
            loop   : 0 loops
        }
        """
        ...
