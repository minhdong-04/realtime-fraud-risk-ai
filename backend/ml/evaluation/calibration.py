"""
{
    module : calibration.py
    desc   : Moduel hiệu chỉnh xác suất (Platt Scaling) và đánh giá chỉ số Brier Score.
}
"""

import numpy as np

def compute_brier_score(y_true: np.ndarray, y_proba: np.ndarray) -> float:
    """
    {
        func   : compute_brier_score
        desc   : Tính chỉ số Brier score đo lường chất lượng hiệu chỉnh xác suất
        input  : y_true (np.ndarray) — nhãn thực tế
                 y_proba (np.ndarray) — xác suất dự đoán
        output : (float) — Brier score (0.0 = hoàn hảo, càng thấp càng tốt)
        loop   : 0 loops — phép toán vector
    }
    """
    return float(np.mean((y_proba - y_true) ** 2))

def platt_scale_probabilities(raw_proba: np.ndarray, a: float = 1.0, b: float = 0.0) -> np.ndarray:
    """
    {
        func   : platt_scale_probabilities
        desc   : Áp dụng biến đổi sigmoid Platt scaling để hiệu chỉnh xác suất dự đoán
        input  : raw_proba (np.ndarray) — xác suất thô
                 a (float) — tham số độ dốc (slope)
                 b (float) — tham số hệ số chặn (intercept)
        output : (np.ndarray) — xác suất đã hiệu chỉnh trong [0.0, 1.0]
        loop   : 0 loops — biến đổi elementwise bằng numpy
    }
    """
    eps = 1e-15
    clipped = np.clip(raw_proba, eps, 1.0 - eps)
    logits = np.log(clipped / (1.0 - clipped))
    calibrated = 1.0 / (1.0 + np.exp(-(a * logits + b)))
    return np.clip(calibrated, 0.0, 1.0)
