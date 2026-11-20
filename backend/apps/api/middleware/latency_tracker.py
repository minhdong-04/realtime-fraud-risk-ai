"""
{
    module : latency_tracker.py
    desc   : Middleware do do tre (latency) thuc te cho moi API request.
             Ghi nhan P50, P95, P99 qua Prometheus Histogram.
}
"""

import time
import logging
from collections import deque
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Luu tru 1000 latency sample gan nhat de tinh P50/P95
_latency_samples: deque[float] = deque(maxlen=1000)


class LatencyTrackerMiddleware(BaseHTTPMiddleware):
    """
    {
        class  : LatencyTrackerMiddleware
        desc   : Middleware do thoi gian xu ly tung API request va ghi nhan Prometheus histogram
    }
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        {
            func   : dispatch
            desc   : Do thoi gian xu ly request va ghi nhan vao Prometheus va bo nho
            input  : request (Request), call_next (callable)
            output : Response
            loop   : 0 loops
        }
        """
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        _latency_samples.append(elapsed)

        # Ghi nhan vao Prometheus histogram
        try:
            from backend.infrastructure.monitoring.prometheus_metrics import metrics
            metrics.observe_latency(elapsed)
        except Exception:
            pass

        response.headers["X-Process-Time"] = f"{elapsed:.4f}"
        return response


def get_latency_stats() -> dict[str, float]:
    """
    {
        func   : get_latency_stats
        desc   : Tinh toan thong ke P50, P95, P99 tu mau latency da ghi nhan
        input  : None
        output : dict — p50, p95, p99, count, avg
        loop   : 0 loops
    }
    """
    if not _latency_samples:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "count": 0, "avg": 0.0}

    import numpy as np
    samples = list(_latency_samples)
    arr = np.array(samples)
    return {
        "p50": round(float(np.percentile(arr, 50)), 4),
        "p95": round(float(np.percentile(arr, 95)), 4),
        "p99": round(float(np.percentile(arr, 99)), 4),
        "count": len(samples),
        "avg": round(float(np.mean(arr)), 4),
    }
