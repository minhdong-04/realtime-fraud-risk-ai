"""
{
    module : risk_engine.py
    desc   : Engine chấm điểm rủi ro lai (Hybrid Risk Engine) kết hợp Supervised ML, Unsupervised Anomaly Detection và Business Rules.
}
"""

import numpy as np
from backend.domain.value_objects.risk_score import RiskScore, RiskLevel
from backend.domain.policies.risk_threshold_policy import RiskThresholdPolicy
from backend.ml.models.base_model import FraudModelStrategy
from backend.ml.models.xgboost_model import XGBoostStrategy
from backend.ml.models.isolation_forest_model import IsolationForestStrategy
from backend.ml.inference.model_loader import load_xgboost_model, load_isolation_forest_model

def compute_hybrid_score(
    fraud_proba: float,
    anomaly_score: float,
    alpha: float = 0.7,
    beta: float = 0.3,
) -> int:
    """
    {
        func   : compute_hybrid_score
        desc   : Kết hợp xác suất XGBoost và điểm dị thường Isolation Forest thành điểm rủi ro 0-100
        input  : fraud_proba (float) — xác suất gian lận XGBoost [0, 1]
                 anomaly_score (float) — điểm dị thường Isolation Forest [0, 1]
                 alpha (float) — trọng số cho XGBoost (mặc định 0.7)
                 beta (float) — trọng số cho Anomaly score (mặc định 0.3)
        output : (int) — điểm rủi ro số nguyên từ 0 đến 100
        loop   : 0 loops
        note   : alpha + beta phải bằng 1.0
    }
    """
    assert abs(alpha + beta - 1.0) < 1e-9, "alpha + beta phải bằng 1.0"
    assert 0.0 <= fraud_proba <= 1.0, "fraud_proba phải nằm trong [0, 1]"
    assert 0.0 <= anomaly_score <= 1.0, "anomaly_score phải nằm trong [0, 1]"

    raw = alpha * fraud_proba + beta * anomaly_score
    return min(100, max(0, round(raw * 100)))

class RiskEngine:
    """
    {
        class  : RiskEngine
        desc   : Bộ điều phối quy trình chấm điểm rủi ro của Risk Engine
        pattern: Strategy + Policy Pattern
    }
    """

    def __init__(
        self,
        supervised_model: FraudModelStrategy | None = None,
        anomaly_model: FraudModelStrategy | None = None,
        policy: RiskThresholdPolicy | None = None,
        alpha: float = 0.7,
        beta: float = 0.3,
    ) -> None:
        self._supervised = supervised_model or XGBoostStrategy(model=load_xgboost_model())
        self._anomaly = anomaly_model or IsolationForestStrategy(model=load_isolation_forest_model())
        self._policy = policy or RiskThresholdPolicy()
        self._alpha = alpha
        self._beta = beta

    def evaluate(
        self,
        features: np.ndarray | dict = None,
        amount: float = 100000.0,
        is_new_device: bool = False,
    ) -> tuple[float, float, RiskScore]:
        """
        {
            func   : evaluate
            desc   : Đánh giá vector đặc trưng và trả về xác suất gian lận, điểm dị thường cùng RiskScore
            input  : features, amount, is_new_device
            output : tuple[fraud_proba, anomaly_score, RiskScore]
            loop   : 0 loops
        }
        """
        if features is None or isinstance(features, dict):
            features_mat = np.zeros((1, 8))
        else:
            features_mat = features

        fraud_proba = self._supervised.predict_proba(features_mat)
        anomaly_score = self._anomaly.get_anomaly_score(features_mat) if self._anomaly else fraud_proba

        numeric_score = compute_hybrid_score(
            fraud_proba=fraud_proba,
            anomaly_score=anomaly_score,
            alpha=self._alpha,
            beta=self._beta,
        )

        level = self._policy.determine_level(
            score=numeric_score,
            amount=amount,
            is_new_device=is_new_device,
        )

        risk_score = RiskScore(value=numeric_score, level=level)
        return fraud_proba, anomaly_score, risk_score
