"""
{
    module : sla_monitoring_service.py
    desc   : Application Service theo dõi và cảnh báo vi phạm SLA 24h kiểm duyệt Case (BR-06).
}
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.infrastructure.db.models.orm_models import FraudCaseORM

class SLAMonitoringService:
    """
    {
        class  : SLAMonitoringService
        desc   : Service quét và phát hiện các Fraud Case sắp hoặc đã quá hạn SLA 24 giờ
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_overdue_cases(self) -> list[FraudCaseORM]:
        """
        {
            func   : get_overdue_cases
            desc   : Lấy danh sách các Fraud Case rủi ro HIGH tạo quá 24h mà chưa đóng
            input  : None
            output : list[FraudCaseORM]
            loop   : 0 loops
        }
        """
        deadline = datetime.now(timezone.utc) - timedelta(hours=24)
        return self._db.query(FraudCaseORM).filter(
            FraudCaseORM.risk_level == "HIGH",
            FraudCaseORM.status != "CLOSED",
            FraudCaseORM.created_at <= deadline,
        ).all()
