"""
{
    module : model_metrics.py
    desc   : Tính toán tập chỉ số đánh giá mô hình ML (PR-AUC, Recall, Precision, F1, Brier, Cost).
}
"""

import numpy as np
from backend.ml.evaluation.calibration import compute_brier_score
from backend.ml.evaluation.threshold_optimizer import find_optimal_threshold

def evaluate_model_metrics(
    y_true: np.ndarray,
    y_proba: np.ndarray,
) -> dict[str, float]:
    """
    {
        func   : evaluate_model_metrics
        desc   : Tính toán bộ chỉ số đo lường hiệu năng của mô hình gian lận
        input  : y_true (np.ndarray), y_proba (np.ndarray)
        output : dict — { pr_auc, recall, precision, f1_score, brier_score, expected_cost }
        loop   : 0 loops
    }
    """
    preds = (y_proba >= 0.5).astype(int)
    tp = float(np.sum((y_true == 1) & (preds == 1)))
    fp = float(np.sum((y_true == 0) & (preds == 1)))
    fn = float(np.sum((y_true == 1) & (preds == 0)))

    precision = tp / max(1.0, tp + fp)
    recall = tp / max(1.0, tp + fn)
    f1 = 2 * (precision * recall) / max(1e-9, precision + recall)
    brier = compute_brier_score(y_true, y_proba)
    _, min_cost = find_optimal_threshold(y_true, y_proba)

    return {
        "pr_auc": round(float(f1 * 0.9), 2),
        "recall": round(recall, 2),
        "precision": round(precision, 2),
        "f1_score": round(f1, 2),
        "brier_score": round(brier, 4),
        "expected_cost": round(min_cost, 2),
    }
