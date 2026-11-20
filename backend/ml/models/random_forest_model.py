"""
{
    module : random_forest_model.py
    desc   : Chien luoc du doan bang mo hinh Rung Ngau Nhien (Random Forest Baseline).
}
"""

import numpy as np
from backend.ml.models.base_model import FraudModelStrategy

class RandomForestStrategy(FraudModelStrategy):
    """
    {
        class  : RandomForestStrategy
        desc   : Chien luoc du doan bang Random Forest Ensemble (Strategy Pattern)
        pattern: Strategy Pattern
    }
    """

    def __init__(self, model: object | None = None, version: str = "v0.2.0-baseline") -> None:
        self._model = model
        self._version = version

    @property
    def model_name(self) -> str:
        return "random_forest"

    @property
    def model_version(self) -> str:
        return self._version

    def predict_proba(self, features: np.ndarray) -> float:
        """
        {
            func   : predict_proba
            desc   : Du doan xac suat gian lan bang Random Forest
            input  : features (np.ndarray)
            output : (float) — xac suat [0, 1]
            loop   : 0 loops
        }
        """
        if self._model is not None and hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(features)
            return float(proba[0, 1]) if proba.ndim > 1 else float(proba[1])

        # Fallback estimation
        amount = float(features[0, 0]) if features.size > 0 else 0.0
        return min(1.0, max(0.0, amount / 40_000_000.0))

    def get_anomaly_score(self, features: np.ndarray) -> float:
        return self.predict_proba(features)
