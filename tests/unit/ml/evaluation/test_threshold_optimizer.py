"""
{
    module : test_threshold_optimizer.py
    desc   : Kiểm thử đơn vị cho Threshold Optimizer (UT-TC-01..04).
}
"""

import numpy as np
from backend.ml.evaluation.threshold_optimizer import compute_expected_cost, find_optimal_threshold

def test_ut_tc_01_compute_expected_cost():
    """UT-TC-01: Tính chi phí bỏ sót gian lận FN và báo sai FP: C_FN*FN + C_FP*FP"""
    y_true = np.array([1, 0, 1, 0])
    y_proba = np.array([0.8, 0.6, 0.3, 0.1])
    cost = compute_expected_cost(y_true, y_proba, threshold=0.5, cost_fn=100.0, cost_fp=1.0)
    assert cost == 101.0

def test_ut_tc_02_find_optimal_threshold():
    """UT-TC-02: Tìm ngưỡng tối ưu hóa tối thiểu chi phí nghiệp vụ"""
    y_true = np.array([1, 1, 0, 0])
    y_proba = np.array([0.9, 0.8, 0.2, 0.1])
    best_th, min_cost = find_optimal_threshold(y_true, y_proba, cost_fn=100.0, cost_fp=1.0)
    assert 0.2 <= best_th <= 0.8
    assert min_cost == 0.0

def test_ut_tc_03_optimal_minimizes_cost():
    """UT-TC-03: Ngưỡng tối ưu phải có expected cost <= expected cost của ngưỡng mặc định 0.5"""
    y_true = np.array([1, 0, 1, 1, 0, 0])
    y_proba = np.array([0.85, 0.45, 0.65, 0.75, 0.25, 0.15])
    best_th, min_cost = find_optimal_threshold(y_true, y_proba, cost_fn=50.0, cost_fp=2.0)
    default_cost = compute_expected_cost(y_true, y_proba, threshold=0.5, cost_fn=50.0, cost_fp=2.0)
    assert min_cost <= default_cost

def test_ut_tc_04_sweep_threshold_range():
    """UT-TC-04: Sweep thresholds trong range [0.1, 0.9] với step 0.01"""
    y_true = np.array([1, 0, 1, 0])
    y_proba = np.array([0.9, 0.7, 0.3, 0.1])
    thresholds = np.arange(0.1, 0.91, 0.01)
    costs = [compute_expected_cost(y_true, y_proba, th) for th in thresholds]
    assert len(costs) == len(thresholds)
    assert min(costs) >= 0.0
