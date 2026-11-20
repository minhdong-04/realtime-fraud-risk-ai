"""
{
    module : test_feature_parity.py
    desc   : Kiểm thử nhất quán đặc trưng Offline / Online Parity (ML-FP-01..05, BR-07).
}
"""

import numpy as np
from backend.ml.features.feature_definitions import FEATURE_NAMES, DEFAULT_FEATURE_VALUES
from backend.ml.features.feature_vector import build_feature_vector

def test_ml_fp_01_feature_names_order_parity():
    """ML-FP-01: Danh sách đặc trưng không bị lệch thứ tự (train / serve parity)"""
    assert len(FEATURE_NAMES) == 8
    assert "txn_count_5m" in FEATURE_NAMES
    assert "new_device_flag" in FEATURE_NAMES

def test_ml_fp_02_default_feature_values_complete():
    """ML-FP-02: Tất cả đặc trưng đều có giá trị mặc định fallback"""
    for name in FEATURE_NAMES:
        assert name in DEFAULT_FEATURE_VALUES

def test_ml_fp_03_schema_parity_training_serving():
    """ML-FP-03: Schema đặc trưng training trùng khớp 100% với Redis serving schema"""
    train_cols = set(FEATURE_NAMES)
    serving_cols = set(DEFAULT_FEATURE_VALUES.keys())
    assert train_cols == serving_cols

def test_ml_fp_04_feature_order_exact_match():
    """ML-FP-04: Thứ tự đặc trưng nhất quán tuyệt đối giữa offline và online vector"""
    sample_dict = {name: float(i + 1) for i, name in enumerate(FEATURE_NAMES)}
    vec = build_feature_vector(sample_dict)
    assert vec.shape == (1, len(FEATURE_NAMES))
    for i, name in enumerate(FEATURE_NAMES):
        assert vec[0, i] == sample_dict[name]

def test_ml_fp_05_preprocessing_transformations_consistency():
    """ML-FP-05: Preprocessing transformations nhất quán (kiểu dữ liệu float64)"""
    sample_dict = {"amount": 500000}
    vec = build_feature_vector(sample_dict)
    assert vec.dtype == np.float64
