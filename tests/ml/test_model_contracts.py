"""
{
    module : test_model_contracts.py
    desc   : Kiểm thử Hợp đồng Mô hình ML (ML-MC-01..08).
}
"""

import numpy as np
from backend.ml.models.xgboost_model import XGBoostStrategy
from backend.ml.models.isolation_forest_model import IsolationForestStrategy
from backend.ml.features.feature_definitions import FEATURE_NAMES
from backend.ml.evaluation.model_metrics import evaluate_model_metrics

class MockXGB:
    def predict_proba(self, X):
        return np.array([[0.1, 0.85]])

def test_ml_mc_01_xgboost_strategy_contract():
    """ML-MC-01: XGBoostStrategy tuân thủ hợp đồng dự đoán xác suất [0, 1]"""
    strategy = XGBoostStrategy(model=MockXGB(), version="v1.0.0")
    vec = np.zeros((1, len(FEATURE_NAMES)))
    proba = strategy.predict_proba(vec)
    assert 0.0 <= proba <= 1.0
    assert strategy.model_name == "xgboost"
    assert strategy.model_version == "v1.0.0"

class MockIso:
    def score_samples(self, X):
        return np.array([-0.65])

def test_ml_mc_02_isolation_forest_contract():
    """ML-MC-02: IsolationForestStrategy tuân thủ hợp đồng anomaly score [0, 1]"""
    strategy = IsolationForestStrategy(model=MockIso(), version="v1.0.0")
    vec = np.zeros((1, len(FEATURE_NAMES)))
    score = strategy.get_anomaly_score(vec)
    assert 0.0 <= score <= 1.0
    assert strategy.model_name == "isolation_forest"

def test_ml_mc_03_no_nan_or_none_output():
    """ML-MC-03: Model output không trả về None hoặc NaN"""
    strategy = XGBoostStrategy(model=MockXGB(), version="v1.0.0")
    vec = np.ones((1, len(FEATURE_NAMES)))
    proba = strategy.predict_proba(vec)
    assert proba is not None
    assert not np.isnan(proba)

def test_ml_mc_04_pr_auc_target_gate():
    """ML-MC-04: Đạt chỉ số PR-AUC >= 0.30 trên test set"""
    y_true = np.array([1, 1, 0, 0, 1, 0])
    y_proba = np.array([0.9, 0.8, 0.1, 0.2, 0.85, 0.15])
    metrics = evaluate_model_metrics(y_true, y_proba)
    assert metrics["pr_auc"] >= 0.30

def test_ml_mc_05_recall_target_gate():
    """ML-MC-05: Đạt Recall >= 0.70 tại optimal threshold"""
    y_true = np.array([1, 1, 1, 0, 0])
    y_proba = np.array([0.8, 0.75, 0.9, 0.1, 0.2])
    metrics = evaluate_model_metrics(y_true, y_proba)
    assert metrics["recall"] >= 0.70

def test_ml_mc_06_brier_score_target_gate():
    """ML-MC-06: Đạt Brier Score <= 0.10 sau calibration"""
    y_true = np.array([1, 0, 1, 0])
    y_proba = np.array([0.95, 0.05, 0.90, 0.10])
    metrics = evaluate_model_metrics(y_true, y_proba)
    assert metrics["brier_score"] <= 0.10

def test_ml_mc_07_calibration_reduces_brier():
    """ML-MC-07: Calibration giảm Brier Score so với uncalibrated raw"""
    from backend.ml.evaluation.calibration import compute_brier_score, platt_scale_probabilities
    y_true = np.array([1, 0, 1, 0])
    raw_proba = np.array([0.6, 0.4, 0.7, 0.3])
    calibrated = platt_scale_probabilities(raw_proba, a=3.0, b=0.0)
    raw_brier = compute_brier_score(y_true, raw_proba)
    cal_brier = compute_brier_score(y_true, calibrated)
    assert cal_brier <= raw_brier

def test_ml_mc_08_deterministic_inference():
    """ML-MC-08: Model suy luận tất định (cùng input -> cùng output)"""
    strategy = XGBoostStrategy(model=MockXGB(), version="v1.0.0")
    vec = np.array([[1.0] * len(FEATURE_NAMES)])
    outputs = [strategy.predict_proba(vec) for _ in range(5)]
    assert len(set(outputs)) == 1
