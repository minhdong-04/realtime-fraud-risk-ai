"""
{
    module : metrics.py
    desc   : Router API xuất các chỉ số Prometheus Metrics tại endpoint /metrics.
}
"""

from fastapi import APIRouter, Response
from backend.infrastructure.monitoring.prometheus_metrics import metrics

router = APIRouter(tags=["Metrics"])

@router.get("/metrics")
def get_prometheus_metrics():
    """
    {
        func   : get_prometheus_metrics
        desc   : Endpoint xuất chỉ số giám sát hệ thống định dạng Prometheus
        input  : None
        output : Response text/plain
        loop   : 0 loops
    }
    """
    data = metrics.generate_exposition()
    return Response(content=data, media_type="text/plain; version=0.0.4")
