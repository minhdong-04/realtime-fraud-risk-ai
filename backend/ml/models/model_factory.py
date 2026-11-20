"""
{
    module : model_factory.py
    desc   : Bộ khởi tạo và tải các phiên bản mô hình ML (Factory Pattern).
}
"""

from backend.ml.models.base_model import FraudModelStrategy
from backend.ml.models.xgboost_model import XGBoostStrategy
from backend.ml.models.isolation_forest_model import IsolationForestStrategy

class ModelFactory:
    """
    {
        class  : ModelFactory
        desc   : Factory Object khởi tạo các mô hình ML theo tên và phiên bản
        pattern: Factory Pattern
    }
    """

    @staticmethod
    def create_model(model_name: str, version: str = "v1.0.0") -> FraudModelStrategy:
        """
        {
            func   : create_model
            desc   : Khởi tạo đối tượng chiến lược mô hình ML
            input  : model_name (str), version (str)
            output : FraudModelStrategy
            loop   : 0 loops
        }
        """
        if model_name == "isolation_forest":
            return IsolationForestStrategy(model=None, version=version)
        return XGBoostStrategy(model=None, version=version)
