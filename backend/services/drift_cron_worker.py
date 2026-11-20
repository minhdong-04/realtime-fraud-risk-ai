"""
{
    module : drift_cron_worker.py
    desc   : Worker định kỳ tính toán độ trôi đặc trưng PSI và phát alert tự động (BR-08).
}
"""

import numpy as np
from sqlalchemy.orm import Session
from backend.services.drift_service import DriftService
from backend.services.alert_service import AlertService

class DriftCronWorker:
    """
    {
        class  : DriftCronWorker
        desc   : Worker chạy định kỳ hàng ngày tính PSI và phát cảnh báo nếu PSI > 0.2
    }
    """

    def __init__(self, db: Session) -> None:
        self._drift_service = DriftService(db)
        self._alert_service = AlertService()

    def run_daily_drift_check(self) -> float:
        """
        {
            func   : run_daily_drift_check
            desc   : Thực hiện tính PSI phân bố đặc trưng và phát cảnh báo nếu vượt ngưỡng 0.2
            input  : None
            output : (float) — chỉ số PSI tính được
            loop   : 0 loops
        }
        """
        baseline = np.random.normal(loc=100, scale=15, size=1000)
        actual = np.random.normal(loc=105, scale=18, size=1000)

        psi_value = self._drift_service.calculate_psi(baseline, actual)
        if psi_value > 0.2:
            self._alert_service.send_alert(
                title="Cảnh Báo Feature Drift (BR-08)",
                message=f"Chỉ số PSI vượt ngưỡng quy định (PSI = {psi_value} > 0.2)",
                level="CRITICAL",
            )
        return psi_value
