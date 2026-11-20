"""
{
    module : model_loader.py
    desc   : Singleton loader cho XGBoost va Isolation Forest model artifacts.
}
"""

import os
import logging
from typing import Any, cast
import numpy as np

logger = logging.getLogger(__name__)

_xgb_model = None
_if_model = None
_models_loaded = False

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
XGB_PATH = os.path.join(ARTIFACTS_DIR, "xgboost_hybrid_v1.0.0.joblib")
IF_PATH = os.path.join(ARTIFACTS_DIR, "isolation_forest_v1.0.0.joblib")


def _ensure_models_loaded() -> None:
    """
    {
        func   : _ensure_models_loaded
        desc   : Tai ca hai model tu disk mot lan duy nhat (Singleton Pattern)
        input  : None
        output : None
        loop   : 0 loops
    }
    """
    global _xgb_model, _if_model, _models_loaded
    if _models_loaded:
        return

    try:
        import joblib
        if os.path.exists(XGB_PATH):
            _xgb_model = joblib.load(XGB_PATH)
            logger.info("Da load XGBoost model tu %s", XGB_PATH)
        else:
            logger.warning("Khong tim thay XGBoost artifact tai %s", XGB_PATH)
    except Exception as exc:
        logger.error("Loi khi load XGBoost model: %s", exc)

    try:
        import joblib
        if os.path.exists(IF_PATH):
            _if_model = joblib.load(IF_PATH)
            logger.info("Da load Isolation Forest model tu %s", IF_PATH)
        else:
            _if_model = _train_default_isolation_forest()
    except Exception as exc:
        logger.error("Loi khi load Isolation Forest: %s", exc)

    _models_loaded = True


def _train_default_isolation_forest():
    """
    {
        func   : _train_default_isolation_forest
        desc   : Train Isolation Forest mac dinh tren phan phoi chuan de phat hien di thuong
        input  : None
        output : IsolationForest model
        loop   : 0 loops
    }
    """
    from sklearn.ensemble import IsolationForest
    import joblib

    rng = np.random.RandomState(42)
    X_normal = rng.randn(5000, 8) * 0.5
    model = IsolationForest(
        n_estimators=100,
        contamination=cast(Any, 0.02),
        random_state=42,
    )
    model.fit(X_normal)
    os.makedirs(os.path.dirname(IF_PATH), exist_ok=True)
    joblib.dump(model, IF_PATH)
    logger.info("Da train va luu Isolation Forest mac dinh tai %s", IF_PATH)
    return model


def load_xgboost_model():
    """
    {
        func   : load_xgboost_model
        desc   : Tra ve XGBoost model da load (None neu khong co artifact)
        input  : None
        output : model hoac None
        loop   : 0 loops
    }
    """
    _ensure_models_loaded()
    return _xgb_model


def load_isolation_forest_model():
    """
    {
        func   : load_isolation_forest_model
        desc   : Tra ve Isolation Forest model da load hoac train mac dinh
        input  : None
        output : IsolationForest model hoac None
        loop   : 0 loops
    }
    """
    _ensure_models_loaded()
    return _if_model
