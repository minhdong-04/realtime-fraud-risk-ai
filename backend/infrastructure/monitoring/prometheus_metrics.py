"""
{
    module : prometheus_metrics.py
    desc   : Khoi tao va ghi nhan cac chi so do luong Prometheus metrics
             su dung thu vien prometheus_client chuan.
}
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

SCORING_REQUESTS: Any = None
SCORING_LATENCY: Any = None
ACTIVE_FRAUD_CASES: Any = None
MODEL_PREDICTIONS: Any = None
generate_latest: Any = None

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest

    SCORING_REQUESTS = Counter(
        "fraud_scoring_requests_total",
        "Tong request cham diem rui ro",
        ["risk_level"],
    )

    SCORING_LATENCY = Histogram(
        "fraud_scoring_latency_seconds",
        "Do tre cham diem rui ro (giay)",
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
    )

    ACTIVE_FRAUD_CASES = Gauge(
        "fraud_active_cases_total",
        "So luong fraud case dang mo",
    )

    MODEL_PREDICTIONS = Counter(
        "fraud_model_predictions_total",
        "Tong so lan du doan model",
        ["model_name"],
    )

    _HAS_PROM_CLIENT = True

except ImportError:
    _HAS_PROM_CLIENT = False
    logger.warning("prometheus_client chua cai dat — dung fallback counter")


class PrometheusMetrics:
    """
    {
        class  : PrometheusMetrics
        desc   : Lop quan ly va xuat cac chi so Prometheus, ho tro ca client that va fallback
    }
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def inc(self, metric_name: str, value: int = 1, labels: dict | None = None) -> None:
        """
        {
            func   : inc
            desc   : Tang bo dem chi so metric
            input  : metric_name (str), value (int), labels (dict)
            output : None
            loop   : 0 loops
        }
        """
        if _HAS_PROM_CLIENT and metric_name == "fraud_scoring_requests_total":
            risk = (labels or {}).get("risk_level", "unknown")
            SCORING_REQUESTS.labels(risk_level=risk).inc(value)
        elif _HAS_PROM_CLIENT and metric_name == "fraud_model_predictions_total":
            name = (labels or {}).get("model_name", "unknown")
            MODEL_PREDICTIONS.labels(model_name=name).inc(value)
        else:
            self._counters[metric_name] = self._counters.get(metric_name, 0) + value

    def observe_latency(self, seconds: float) -> None:
        """
        {
            func   : observe_latency
            desc   : Ghi nhan thoi gian xu ly request vao histogram
            input  : seconds (float)
            output : None
            loop   : 0 loops
        }
        """
        if _HAS_PROM_CLIENT:
            SCORING_LATENCY.observe(seconds)

    def generate_exposition(self) -> str:
        """
        {
            func   : generate_exposition
            desc   : Tra ve chuoi noi dung dinh dang Prometheus exposition text
            input  : None
            output : (str)
            loop   : 1 loop
        }
        """
        if _HAS_PROM_CLIENT and generate_latest is not None:
            return generate_latest().decode("utf-8")

        lines = []
        # { loop-1: dinh dang tung dong chi so metric fallback }
        for k, v in self._counters.items():
            lines.append(f"# TYPE {k} counter\n{k} {v}")
        return "\n".join(lines) or "# Prometheus Metrics OK\n"


metrics = PrometheusMetrics()
