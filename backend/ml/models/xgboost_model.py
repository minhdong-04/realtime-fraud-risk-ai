"""
{
    module : xgboost_model.py
    desc   : Cài đặt Chiến lược Mô hình XGBoost (Concrete Strategy).
}
"""

import numpy as np
from backend.ml.models.base_model import FraudModelStrategy

class XGBoostStrategy(FraudModelStrategy):
    """
    {
        class  : XGBoostStrategy
        desc   : Concrete Strategy sử dụng thuật toán XGBoost cho phân loại gian lận
        pattern: Strategy Pattern
    }
    """

    def __init__(self, model: any = None, version: str = "v1.0.0") -> None:
        self._model = model
        self._version = version

    def predict_proba(self, features: np.ndarray) -> float:
        """
        {
            func   : predict_proba
            desc   : Tính xác suất gian lận bằng bộ phân loại XGBoost
            input  : features (np.ndarray) — shape (1, n_features)
            output : (float) — xác suất [0, 1]
            loop   : 0 loops
        }
        """
        if self._model is None:
            import warnings
            warnings.warn("XGBoost model chua duoc load — su dung fallback 0.1")
            return 0.1

        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(features)
            val = float(proba[0, 1])
        elif hasattr(self._model, "predict"):
            val = float(self._model.predict(features)[0])
        else:
            val = 0.1

        return max(0.0, min(1.0, val))

    def get_anomaly_score(self, features: np.ndarray) -> float:
        """
        {
            func   : get_anomaly_score
            desc   : Trả về xác suất gian lận làm giá trị đại diện cho anomaly score của XGBoost
            input  : features (np.ndarray)
            output : (float) — điểm rủi ro [0, 1]
            loop   : 0 loops
        }
        """
        return self.predict_proba(features)

    @property
    def model_name(self) -> str:
        return "xgboost"

    @property
    def model_version(self) -> str:
        return self._version
