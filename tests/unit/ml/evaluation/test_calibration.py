"""
{
    module : test_calibration.py
    desc   : Kiểm thử đơn vị cho Platt Scaling & Brier Score (UT-CAL-01..03).
}
"""

import numpy as np
from backend.ml.evaluation.calibration import compute_brier_score, platt_scale_probabilities

def test_ut_cal_01_compute_brier_score_perfect():
    """UT-CAL-01: Brier score = 0.0 khi dự đoán hoàn hảo"""
    y_true = np.array([1, 0, 1, 0])
    y_proba = np.array([1.0, 0.0, 1.0, 0.0])
    assert compute_brier_score(y_true, y_proba) == 0.0

def test_ut_cal_02_platt_scale_probabilities():
    """UT-CAL-02: Biến đổi Platt scale nằm trong khoảng [0, 1]"""
    raw = np.array([0.1, 0.5, 0.9])
    scaled = platt_scale_probabilities(raw, a=1.0, b=0.0)
    assert np.all(scaled >= 0.0) and np.all(scaled <= 1.0)

def test_ut_cal_03_monotonic_ranking_conservation():
    """UT-CAL-03: Calibration giữ nguyên thứ tự ranking giữa các mẫu (Đơn điệu tăng)"""
    raw = np.array([0.1, 0.3, 0.6, 0.85])
    calibrated = platt_scale_probabilities(raw, a=2.0, b=0.0)
    # Kiểm tra thứ tự tăng dần được bảo toàn
    assert np.all(np.diff(calibrated) >= 0)
