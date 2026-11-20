"""
{
    module : threshold_optimizer.py
    desc   : Module tối ưu hóa ngưỡng quyết định dựa trên Ma trận Chi phí Nghiệp vụ (Business Cost Matrix).
}
"""

import numpy as np

def compute_expected_cost(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    threshold: float,
    cost_fn: float = 100.0,
    cost_fp: float = 1.0,
) -> float:
    """
    {
        func   : compute_expected_cost
        desc   : Tính tổng chi phí nghiệp vụ kỳ vọng ứng với một ngưỡng quyết định cụ thể
        input  : y_true (np.ndarray) — nhãn gian lận thực tế (1 = gian lận, 0 = hợp lệ)
                 y_proba (np.ndarray) — xác suất gian lận dự đoán
                 threshold (float) — ngưỡng phân loại
                 cost_fn (float) — chi phí bỏ sót gian lận (False Negative)
                 cost_fp (float) — chi phí cảnh báo sai (False Positive)
        output : (float) — tổng chi phí nghiệp vụ kỳ vọng
        loop   : 0 loops — phép toán boolean mask trên numpy
    }
    """
    preds = (y_proba >= threshold).astype(int)
    fn = np.sum((y_true == 1) & (preds == 0))
    fp = np.sum((y_true == 0) & (preds == 1))
    return float(cost_fn * fn + cost_fp * fp)

def find_optimal_threshold(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    cost_fn: float = 100.0,
    cost_fp: float = 1.0,
) -> tuple[float, float]:
    """
    {
        func   : find_optimal_threshold
        desc   : Quét các ngưỡng trong [0.10, 0.90] để tìm ngưỡng tối ưu hóa tối thiểu chi phí nghiệp vụ
        input  : y_true (np.ndarray)
                 y_proba (np.ndarray)
                 cost_fn (float)
                 cost_fp (float)
        output : tuple[optimal_threshold, min_cost]
        loop   : 1 loop — quét lưới (grid search) qua các ngưỡng ứng viên
    }
    """
    thresholds = np.linspace(0.1, 0.9, 81)
    best_threshold = 0.5
    min_cost = float("inf")

    # { loop-1: quét qua danh sách các ngưỡng ứng viên }
    for th in thresholds:
        cost = compute_expected_cost(y_true, y_proba, float(th), cost_fn, cost_fp)
        if cost < min_cost:
            min_cost = cost
            best_threshold = float(th)

    return best_threshold, min_cost
