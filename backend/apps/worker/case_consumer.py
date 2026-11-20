"""
{
    module : case_consumer.py
    desc   : Worker Consumer lắng nghe risk.scored để tự động mở Fraud Case cho giao dịch HIGH risk.
}
"""

from typing import Any
from sqlalchemy.orm import Session
from backend.services.fraud_case_service import FraudCaseService

class CaseConsumer:
    """
    {
        class  : CaseConsumer
        desc   : Worker xử lý tự động tạo Fraud Case khi phát hiện mức rủi ro HIGH
    }
    """

    def __init__(self, db: Session) -> None:
        self._service = FraudCaseService(db)

    def process_event(self, event_data: dict[str, Any]) -> Any:
        """
        {
            func   : process_event
            desc   : Kiểm tra nếu rủi ro HIGH thì tạo Fraud Case mới
            input  : event_data (dict)
            output : FraudCaseORM | None
            loop   : 0 loops
        }
        """
        risk_level = event_data.get("risk_level", "LOW")
        if risk_level == "HIGH":
            txn_id = event_data.get("transaction_id", "")
            return self._service.create_case_if_high_risk(txn_id, risk_level, event_data.get("score", 0.9))
        return None
