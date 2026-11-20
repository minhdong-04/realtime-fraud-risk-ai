"""
{
    module : analytics.py
    desc   : Router API Báo cáo thống kê Analytics dành cho Risk Manager (US-04, US-10).
}
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from backend.infrastructure.db.session import get_db
from backend.services.analytics_service import AnalyticsService
from backend.services.report_service import ReportService
from backend.services.drift_service import DriftService
from backend.apps.api.dependencies import get_current_user
from backend.apps.api.middleware.latency_tracker import get_latency_stats

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/fraud")
@router.get("/dashboard")
def get_fraud_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_fraud_analytics
        desc   : Lấy các chỉ số KPI, biểu đồ phân bố rủi ro và biểu đồ xu hướng cho Manager Dashboard (US-04)
        input  : db (Session)
        output : dict — dữ liệu chỉ số analytics
        loop   : 0 loops
    }
    """
    service = AnalyticsService(db)
    return service.get_dashboard_metrics()

@router.get("/drift")
def get_model_drift_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_model_drift_metrics
        desc   : Lấy báo cáo chỉ số trôi đặc trưng PSI và trạng thái cảnh báo Data Drift (US-08)
        input  : db (Session)
        output : dict — { overall_psi, status, feature_drift_list }
        loop   : 0 loops
    }
    """
    import numpy as np
    from backend.infrastructure.db.models.orm_models import ModelPredictionORM

    drift_service = DriftService(db)

    # Lay score tu DB de tinh PSI thuc te
    predictions = db.query(ModelPredictionORM.fraud_probability).order_by(
        ModelPredictionORM.id.desc()
    ).limit(2000).all()
    scores = [p[0] for p in predictions if p[0] is not None]

    if len(scores) >= 100:
        mid = len(scores) // 2
        expected = np.array(scores[:mid])
        actual = np.array(scores[mid:])
        overall_psi = drift_service.calculate_psi(expected, actual)
    else:
        overall_psi = 0.0

    status = "DRIFTED" if overall_psi > 0.2 else "HEALTHY"
    return {
        "overall_psi": overall_psi,
        "status": status,
        "threshold": 0.2,
        "sample_count": len(scores),
    }

@router.get("/latency")
def get_inference_latency_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_inference_latency_metrics
        desc   : Lấy các chỉ số độ trễ chấm điểm thời gian thực P50, P95, P99 (US-07)
        input  : db (Session)
        output : dict — { p50_ms, p95_ms, p99_ms, target_p95_ms }
        loop   : 0 loops
    }
    """
    stats = get_latency_stats()
    p95_ms = stats["p95"] * 1000
    return {
        "p50_ms": round(stats["p50"] * 1000, 1),
        "p95_ms": round(p95_ms, 1),
        "p99_ms": round(stats["p99"] * 1000, 1),
        "avg_ms": round(stats["avg"] * 1000, 1),
        "sample_count": stats["count"],
        "target_p95_ms": 100.0,
        "status": "NORMAL" if p95_ms < 100 else "WARNING",
    }

@router.get("/export")
@router.post("/export")
def export_csv_report(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : export_csv_report
        desc   : Trích xuất tệp báo cáo tổng hợp gian lận định dạng CSV (US-10)
        input  : db (Session)
        output : Response đính kèm file CSV để tải về
        loop   : 0 loops
    }
    """
    report_service = ReportService(db)
    csv_data = report_service.export_csv_report()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fraud_summary_report.csv"},
    )
