"""
{
    module : scorer.py
    desc   : Cài đặt bộ chấm điểm (Scorer) sử dụng Decorator Pattern để hỗ trợ caching và chịu lỗi.
}
"""

import hashlib
from typing import Any
import numpy as np
from backend.ml.models.base_model import FraudModelStrategy

class RealScorer:
    """
    {
        class  : RealScorer
        desc   : Scorer lõi bọc trực tiếp hàm dự đoán của mô hình ML
        pattern: Component trong chuỗi Decorator
    }
    """

    def __init__(self, model: FraudModelStrategy) -> None:
        self._model = model

    def score(self, features: np.ndarray) -> float:
        """
        {
            func   : score
            desc   : Thực thi dự đoán predict_proba từ model
            input  : features (np.ndarray)
            output : (float) — xác suất gian lận
            loop   : 0 loops
        }
        """
        return self._model.predict_proba(features)

class CachingScorer:
    """
    {
        class  : CachingScorer
        desc   : Decorator hỗ trợ lưu cache kết quả chấm điểm theo mã hash của đặc trưng
        pattern: Decorator Pattern
    }
    """

    def __init__(self, wrapped: RealScorer, cache_adapter: Any = None, ttl: int = 300) -> None:
        self._wrapped = wrapped
        self._cache = cache_adapter
        self._ttl = ttl

    def score(self, features: np.ndarray) -> float:
        """
        {
            func   : score
            desc   : Kiểm tra cache trước khi gọi scorer thực sự
            input  : features (np.ndarray)
            output : (float) — xác suất gian lận từ cache hoặc từ model
            loop   : 0 loops
        }
        """
        if self._cache is not None:
            cache_key = f"score:{hashlib.md5(features.tobytes()).hexdigest()}"
            cached_val = self._cache.get(cache_key)
            if cached_val is not None:
                return float(cached_val)

        result = self._wrapped.score(features)

        if self._cache is not None:
            cache_key = f"score:{hashlib.md5(features.tobytes()).hexdigest()}"
            self._cache.set(cache_key, result, ttl=self._ttl)

        return result
