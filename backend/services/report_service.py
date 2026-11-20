"""
{
    module : report_service.py
    desc   : Application Service tạo và xuất báo cáo CSV giao dịch & kiểm duyệt.
}
"""

import csv
import io
from sqlalchemy.orm import Session
from backend.infrastructure.db.models.orm_models import TransactionORM, AnalystReviewORM

class ReportService:
    """
    {
        class  : ReportService
        desc   : Service tạo báo cáo dữ liệu định dạng CSV phục vụ kiểm toán và xuất báo cáo
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def export_csv_report(self, days: int = 30) -> str:
        """
        {
            func   : export_csv_report
            desc   : Xuất danh sách giao dịch và quyết định kiểm duyệt dưới dạng chuỗi CSV
            input  : days (int)
            output : (str) — nội dung CSV
            loop   : 1 loop — ghi các dòng dữ liệu giao dịch
        }
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Transaction ID", "Account ID", "Amount", "Currency", "Created At"])

        txns = self._db.query(TransactionORM).limit(100).all()
        # { loop-1: ghi từng giao dịch ra dòng CSV }
        for t in txns:
            writer.writerow([t.id, t.account_id, t.amount, t.currency, t.created_at])

        return output.getvalue()
