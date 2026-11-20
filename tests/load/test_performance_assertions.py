"""
{
    module : test_performance_assertions.py
    desc   : Kiem thu khang dinh chi tieu hieu nang Latency P95 < 100ms theo BA 3 va 03_SENIOR_TEST_PLAN.
}
"""

import time
import pytest
from backend.ml.inference.risk_engine import RiskEngine
from backend.ml.features.feature_definitions import FEATURE_NAMES
import numpy as np

def test_inference_latency_under_100ms():
    """PERF-01: Thoi gian thuc thi Risk Engine danh gia 1 vector phai < 100ms (P95 SLA)"""
    engine = RiskEngine()
    features = np.zeros((1, len(FEATURE_NAMES)))

    latencies = []
    # { loop-1: chay 50 lan suy luan de do do tre }
    for _ in range(50):
        start = time.perf_counter()
        engine.evaluate(features=features, amount=500000.0, is_new_device=False)
        duration_ms = (time.perf_counter() - start) * 1000.0
        latencies.append(duration_ms)

    p95_latency = np.percentile(latencies, 95)
    assert p95_latency < 100.0, f"Latency P95 = {p95_latency:.2f}ms vuot qua nguong SLA 100ms"

def test_feature_vector_build_under_10ms():
    """PERF-02: Thoi gian tao feature vector phai < 10ms"""
    from backend.ml.features.feature_vector import build_feature_vector
    sample_dict = {"amount": 100000.0}

    start = time.perf_counter()
    vec = build_feature_vector(sample_dict)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert duration_ms < 10.0
    assert vec.shape == (1, 8)
