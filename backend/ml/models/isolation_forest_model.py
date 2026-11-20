"""
{
    module : isolation_forest_model.py
    desc   : Cài đặt Chiến lược Mô hình Isolation Forest (Concrete Strategy).
}
"""

from typing import Any
import numpy as np
from backend.ml.models.base_model import FraudModelStrategy

class IsolationForestStrategy(FraudModelStrategy):
    """
    {
        class  : IsolationForestStrategy
        desc   : Concrete Strategy sử dụng Isolation Forest cho chấm điểm bất thường (Unsupervised Anomaly Scoring)
        pattern: Strategy Pattern
    }
    """

    def __init__(self, model: Any = None, version: str = "v1.0.0") -> None:
        self._model = model
        self._version = version

    def predict_proba(self, features: np.ndarray) -> float:
        """
        {
            func   : predict_proba
            desc   : Trả về điểm dị thường được chuẩn hóa làm ước lượng xác suất
            input  : features (np.ndarray) — shape (1, n_features)
            output : (float) — xác suất [0, 1]
            loop   : 0 loops
        }
        """
        return self.get_anomaly_score(features)

    def get_anomaly_score(self, features: np.ndarray) -> float:
        """
        {
            func   : get_anomaly_score
            desc   : Tính điểm dị thường được chuẩn hóa từ decision function
            input  : features (np.ndarray)
            output : (float) — điểm rủi ro [0, 1] với 1.0 là cực kỳ bất thường
            loop   : 0 loops
        }
        """
        if self._model is None:
            import warnings
            warnings.warn("Isolation Forest chua duoc load — su dung fallback 0.15")
            return 0.15

        if hasattr(self._model, "score_samples"):
            raw = self._model.score_samples(features)[0]
            score = max(0.0, min(1.0, -float(raw)))
        elif hasattr(self._model, "decision_function"):
            raw = self._model.decision_function(features)[0]
            score = max(0.0, min(1.0, 0.5 - float(raw)))
        else:
            score = 0.15
        return score

    @property
    def model_name(self) -> str:
        return "isolation_forest"

    @property
    def model_version(self) -> str:
        return self._version
