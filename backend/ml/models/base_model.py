"""
{
    module : base_model.py
    desc   : Interface abstract cho Chiến lược Mô hình Gian lận ML (Strategy Pattern).
}
"""

from abc import ABC, abstractmethod
import numpy as np

class FraudModelStrategy(ABC):
    """
    {
        class  : FraudModelStrategy
        desc   : Interface trừu tượng cho tất cả các mô hình Machine Learning trong hệ thống
        pattern: Strategy Pattern
    }
    """

    @abstractmethod
    def predict_proba(self, features: np.ndarray) -> float:
        """
        {
            func   : predict_proba
            desc   : Dự đoán xác suất gian lận cho vector đặc trưng
            input  : features (np.ndarray) — shape (1, n_features)
            output : (float) — xác suất gian lận trong khoảng [0.0, 1.0]
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def get_anomaly_score(self, features: np.ndarray) -> float:
        """
        {
            func   : get_anomaly_score
            desc   : Tính điểm dị thường được chuẩn hóa
            input  : features (np.ndarray) — shape (1, n_features)
            output : (float) — điểm dị thường trong khoảng [0.0, 1.0] (1.0 = rất bất thường)
            loop   : 0 loops
        }
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    @property
    @abstractmethod
    def model_version(self) -> str:
        ...
