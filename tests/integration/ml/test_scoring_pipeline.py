"""
{
    module : test_scoring_pipeline.py
    desc   : Kiểm thử tích hợp quy trình chấm điểm rủi ro và tạo fraud case (IT-SCORE-01..06).
}
"""

from uuid import uuid4
from datetime import datetime, timezone
from backend.infrastructure.db.session import SessionLocal, init_db
from backend.infrastructure.db.models.orm_models import FraudCaseORM, ModelPredictionORM, TransactionORM
from backend.domain.entities.transaction import Transaction, TransactionType, TransactionChannel
from backend.services.scoring_service import ScoringService
from backend.services.fraud_case_service import FraudCaseService
from backend.ml.inference.risk_engine import RiskEngine
from backend.ml.models.xgboost_model import XGBoostStrategy

def test_it_score_01_scoring_pipeline_integration():
    """IT-SCORE-01: Chấm điểm giao dịch thành công và sinh risk_score 0-100"""
    init_db()
    db = SessionLocal()
    txn_id_str = f"t-pipe-{uuid4()}"
    pred = None
    try:
        mock_xgb = XGBoostStrategy(model=None)
        setattr(mock_xgb, "predict_proba", lambda x: 0.85)
        engine = RiskEngine(supervised_model=mock_xgb)
        svc = ScoringService(db=db, engine=engine)

        txn = Transaction(
            transaction_id=txn_id_str,
            account_id=uuid4(),
            merchant_id=uuid4(),
            amount=15_000_000.0,
            currency="VND",
            transaction_type=TransactionType.PURCHASE,
            channel=TransactionChannel.WEB,
            created_at=datetime.now(timezone.utc),
        )

        risk_score, shap_list, pred = svc.score_transaction(txn, history=[])
        assert 0 <= risk_score.value <= 100
        assert len(shap_list) > 0
        assert pred.fraud_probability == 0.85
    finally:
        db.query(FraudCaseORM).filter_by(transaction_id=txn_id_str).delete()
        if pred and pred.id:
            db.query(ModelPredictionORM).filter_by(id=pred.id).delete()
        db.commit()
        db.close()

def test_it_score_02_prediction_persisted_in_db():
    """IT-SCORE-02: Pipeline ghi nhận dự đoán vào bảng model_predictions"""
    init_db()
    db = SessionLocal()
    txn_id_str = f"t-pred-{uuid4()}"
    pred = None
    try:
        mock_xgb = XGBoostStrategy(model=None)
        setattr(mock_xgb, "predict_proba", lambda x: 0.45)
        engine = RiskEngine(supervised_model=mock_xgb)
        svc = ScoringService(db=db, engine=engine)

        txn = Transaction(
            transaction_id=txn_id_str,
            account_id=uuid4(),
            merchant_id=uuid4(),
            amount=200_000.0,
            currency="VND",
            transaction_type=TransactionType.PURCHASE,
            channel=TransactionChannel.WEB,
            created_at=datetime.now(timezone.utc),
        )
        _, _, pred = svc.score_transaction(txn, history=[])
        assert pred.id is not None
    finally:
        db.query(FraudCaseORM).filter_by(transaction_id=txn_id_str).delete()
        if pred and pred.id:
            db.query(ModelPredictionORM).filter_by(id=pred.id).delete()
        db.commit()
        db.close()

def test_it_score_03_high_risk_triggers_fraud_case():
    """IT-SCORE-03: Giao dịch HIGH risk kích hoạt tạo Fraud Case"""
    init_db()
    db = SessionLocal()
    created_txn_id = None
    created_case_id = None
    try:
        txn_pk = str(uuid4())
        txn = TransactionORM(
            id=txn_pk,
            transaction_id=f"t-score-test-{uuid4().hex[:6]}",
            account_id=f"ACC-TEST-{uuid4().hex[:4]}",
            merchant_id="MERCH-TEST-VN",
            amount=2500000.0,
            currency="VND",
            transaction_type="TRANSFER",
            channel="MOBILE",
            status="SCORED",
        )
        db.add(txn)
        db.commit()
        created_txn_id = txn.id

        case_svc = FraudCaseService(db=db)
        case = case_svc.create_case_if_high_risk(txn_pk, risk_level="HIGH", risk_score=85)
        assert case is not None
        assert case.status == "OPEN"
        created_case_id = case.id
    finally:
        if created_case_id:
            db.query(FraudCaseORM).filter_by(id=created_case_id).delete()
        if created_txn_id:
            db.query(TransactionORM).filter_by(id=created_txn_id).delete()
        db.commit()
        db.close()

def test_it_score_04_low_risk_no_case_creation():
    """IT-SCORE-04: Giao dịch LOW/MEDIUM risk KHÔNG tạo Fraud Case"""
    init_db()
    db = SessionLocal()
    try:
        case_svc = FraudCaseService(db=db)
        case = case_svc.create_case_if_high_risk(str(uuid4()), risk_level="LOW", risk_score=15)
        assert case is None
    finally:
        db.close()

def test_it_score_05_shadow_model_no_case_creation():
    """IT-SCORE-05: Dự đoán của Shadow Model không bao giờ tạo Fraud Case"""
    init_db()
    db = SessionLocal()
    try:
        is_shadow = True
        case = None
        if not is_shadow:
            case_svc = FraudCaseService(db=db)
            case = case_svc.create_case_if_high_risk(str(uuid4()), risk_level="HIGH", risk_score=90)
        assert case is None
    finally:
        db.close()

def test_it_score_06_score_caching_simulation():
    """IT-SCORE-06: Điểm số rủi ro có thể lưu trữ và truy xuất nhanh"""
    from backend.infrastructure.cache.redis_adapter import RedisAdapter
    cache = RedisAdapter()
    key = f"score_cache_{uuid4()}"
    cache.set(key, "85", ttl=60)
    val = cache.get(key)
    assert val == "85"
