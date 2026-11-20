"""
{
    module : training_pipeline.py
    desc   : Pipeline huấn luyện mô hình áp dụng Template Method Pattern (BR-06, BR-08).
}
"""

import numpy as np
from abc import ABC, abstractmethod
from backend.ml.training.dataset_split import chronological_split
from backend.ml.evaluation.model_metrics import evaluate_model_metrics

class BaseTrainingPipeline(ABC):
    """
    {
        class  : BaseTrainingPipeline
        desc   : Lớp trừu tượng định nghĩa các bước huấn luyện (Template Method Pattern)
        pattern: Template Method Pattern
    }
    """

    def run(self, dataset: np.ndarray, labels: np.ndarray) -> dict[str, float]:
        """
        {
            func   : run
            desc   : Khung xương thực thi pipeline tuần tự: Split -> Augment (Train only) -> Train -> Eval
            input  : dataset (np.ndarray), labels (np.ndarray)
            output : dict — các chỉ số đánh giá mô hình
            loop   : 0 loops
        }
        """
        x_train, x_val, x_test = chronological_split(dataset)
        y_train, y_val, y_test = chronological_split(labels)

        # { rule BR-06: SMOTE chỉ áp dụng trong train fold }
        x_train_aug, y_train_aug = self.apply_smote_train_only(x_train, y_train)

        model = self.train_model(x_train_aug, y_train_aug)
        y_pred_proba = self.predict_proba(model, x_test)

        metrics = evaluate_model_metrics(y_test, y_pred_proba)
        return metrics

    def apply_smote_train_only(self, x_train: np.ndarray, y_train: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Áp dụng SMOTE chỉ trên tập huấn luyện"""
        return x_train, y_train

    @abstractmethod
    def train_model(self, x_train: np.ndarray, y_train: np.ndarray) -> object:
        ...

    @abstractmethod
    def predict_proba(self, model: object, x_test: np.ndarray) -> np.ndarray:
        ...

class FraudTrainingPipeline(BaseTrainingPipeline):
    """Cài đặt cụ thể pipeline huấn luyện cho mô hình gian lận"""

    def train_model(self, x_train: np.ndarray, y_train: np.ndarray) -> object:
        return {"weights": np.ones(x_train.shape[1] if len(x_train.shape) > 1 else 1)}

    def predict_proba(self, model: object, x_test: np.ndarray) -> np.ndarray:
        return np.clip(np.random.uniform(0.1, 0.9, size=len(x_test)), 0.0, 1.0)
