"""
{
    module : feature_vector.py
    desc   : Đóng gói và chuẩn hóa mảng đặc trưng numpy cho ML inference.
}
"""

import numpy as np
from typing import Mapping
from backend.ml.features.feature_definitions import FEATURE_NAMES

def build_feature_vector(features: Mapping[str, float]) -> np.ndarray:
    """
    {
        func   : build_feature_vector
        desc   : Chuyển đổi dictionary đặc trưng thành mảng numpy shape (1, n_features) đúng thứ tự
        input  : features (Mapping[str, float])
        output : (np.ndarray) — ma trận 2D numpy
        loop   : 1 loop — sắp xếp theo đúng thứ tự FEATURE_NAMES
    }
    """
    # { loop-1: duyệt qua FEATURE_NAMES để giữ thứ tự chuẩn }
    values = [float(features.get(name, 0.0)) for name in FEATURE_NAMES]
    return np.array([values], dtype=np.float64)
