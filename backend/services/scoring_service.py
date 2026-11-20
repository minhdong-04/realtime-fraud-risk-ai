"""
{
    module : scoring_service.py
    desc   : Application Service điều phối tính toán đặc trưng trực tuyến và chấm điểm rủi ro.
}
"""

from typing import Any
from uuid import uuid4
import numpy as np
from sqlalchemy.orm import Session

from backend.domain.entities.transaction import Transaction
from backend.domain.value_objects.risk_score import RiskScore, RiskLevel
from backend.domain.exceptions import ScoringError
from backend.ml.features.feature_definitions import FEATURE_NAMES
from backend.ml.features.velocity_features import (
    compute_txn_count_5m, compute_txn_count_1h, compute_amount_sum_1h, compute_unique_merchants_1h
)
from backend.ml.features.behavioural_features import compute_avg_amount_30d, compute_amount_ratio
from backend.ml.features.novelty_features import compute_new_device_flag, compute_new_merchant_flag
from backend.ml.inference.risk_engine import RiskEngine
from backend.ml.inference.shap_explainer import generate_shap_explanation
from backend.infrastructure.db.models.orm_models import ModelPredictionORM, TransactionORM, FraudCaseORM
from backend.infrastructure.cache.redis_adapter import RedisAdapter

class ScoringService:
    """
    {
        class  : ScoringService
        desc   : Application service thực thi pipeline trích xuất đặc trưng và đánh giá rủi ro lai (Hybrid Risk Engine)
        pattern: Application Service
    }
    """

    def __init__(self, db: Session, engine: RiskEngine | None = None, cache: RedisAdapter | None = None) -> None:
        self._db = db
        self._engine = engine or RiskEngine()
        self._cache = cache or RedisAdapter()

    def score_transaction(
        self,
        transaction: Transaction | dict,
        history: list[Transaction] | None = None,
    ) -> tuple[RiskScore, list[dict[str, Any]], ModelPredictionORM]:
        """
        {
            func   : score_transaction
            desc   : Thực thi pipeline tính toán đặc trưng, chạy risk engine, lưu dự đoán và tự động tạo fraud case nếu rủi ro HIGH hoặc MEDIUM
            input  : transaction (Transaction | dict), history (list[Transaction] | None)
            output : tuple[RiskScore, danh_sách_shap, bản_ghi_dự_đoán]
            loop   : 1 loop — chuyển dictionary đặc trưng thành mảng numpy
            throws : ScoringError khi đánh giá rủi ro thất bại
        }
        """
        try:
            hist_list = history or []
            if isinstance(transaction, dict):
                amount = float(transaction.get("amount", 100000.0))
                txn_id = transaction.get("transaction_id", str(uuid4()))
                account_id = transaction.get("account_id", str(uuid4()))
                device_id = transaction.get("device_id")
                merchant_id = transaction.get("merchant_id")
                from datetime import datetime, timezone
                created_at = datetime.now(timezone.utc)
            else:
                amount = transaction.amount
                txn_id = transaction.transaction_id
                account_id = str(transaction.account_id)
                device_id = transaction.device_id
                merchant_id = transaction.merchant_id
                created_at = transaction.created_at

            # 1. Trích xuất đặc trưng (Feature Engineering)
            v_5m = compute_txn_count_5m(hist_list, created_at)
            v_1h = compute_txn_count_1h(hist_list, created_at)
            sum_1h = compute_amount_sum_1h(hist_list, created_at)
            uniq_merch = compute_unique_merchants_1h(hist_list, created_at)
            avg_30d = compute_avg_amount_30d(hist_list)
            ratio = compute_amount_ratio(amount, avg_30d)
            new_device = compute_new_device_flag(device_id, hist_list)
            new_merchant = compute_new_merchant_flag(merchant_id, hist_list)

            features_dict = {
                "txn_count_5m": v_5m,
                "txn_count_1h": v_1h,
                "amount_sum_1h": sum_1h,
                "unique_merchants_1h": uniq_merch,
                "avg_amount_30d": avg_30d,
                "amount_ratio": ratio,
                "new_device_flag": new_device,
                "new_merchant_flag": new_merchant,
            }

            self._cache.set_features(account_id, features_dict)

            # { loop-1: tạo mảng đặc trưng chuẩn hóa theo thứ tự FEATURE_NAMES }
            feature_vector = np.array([[float(features_dict[name]) for name in FEATURE_NAMES]])

            # 2. Đánh giá rủi ro qua Risk Engine
            fraud_proba, anomaly_score, risk_score = self._engine.evaluate(
                features=feature_vector,
                amount=amount,
                is_new_device=bool(new_device),
            )

            # 3. Tạo giải thích SHAP
            shap_list = generate_shap_explanation(features_dict, fraud_proba)

            # 4. Lưu bản ghi kết quả dự đoán
            pred_orm = ModelPredictionORM(
                transaction_id=str(getattr(transaction, 'id', txn_id)),
                model_name=self._engine._supervised.model_name,
                model_version=self._engine._supervised.model_version,
                fraud_probability=fraud_proba,
                anomaly_score=anomaly_score,
                risk_score=risk_score.value,
                risk_level=risk_score.level.value,
                threshold_used=0.5,
                shap_values=shap_list,
                is_shadow=False,
            )
            self._db.add(pred_orm)

            # 5. Cập nhật trạng thái transaction nếu có trong DB
            txn_orm = self._db.query(TransactionORM).filter_by(transaction_id=txn_id).first()
            if txn_orm:
                txn_orm.status = "SCORED"

            # 6. Tự động tạo Fraud Case nếu rủi ro HIGH hoặc MEDIUM (BR-04)
            if risk_score.level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                existing_case = self._db.query(FraudCaseORM).filter_by(transaction_id=str(getattr(transaction, 'id', txn_id))).first()
                if not existing_case:
                    case_orm = FraudCaseORM(
                        transaction_id=str(getattr(transaction, 'id', txn_id)),
                        risk_level=risk_score.level.value,
                        risk_score=risk_score.value,
                        status="OPEN",
                    )
                    self._db.add(case_orm)

                    # A4: Broadcast qua WebSocket khi tao fraud case moi
                    try:
                        import asyncio
                        from backend.apps.api.routers.websocket import ws_manager
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            loop = None
                        if loop and loop.is_running():
                            loop.create_task(ws_manager.broadcast({
                                "type": "NEW_FRAUD_CASE",
                                "transaction_id": str(getattr(transaction, 'id', txn_id)),
                                "risk_level": risk_score.level.value,
                                "risk_score": risk_score.value,
                            }))
                    except Exception:
                        pass

            self._db.commit()
            return risk_score, shap_list, pred_orm

        except Exception as e:
            self._db.rollback()
            raise ScoringError(f"Quy trình chấm điểm thất bại cho giao dịch: {e}")
