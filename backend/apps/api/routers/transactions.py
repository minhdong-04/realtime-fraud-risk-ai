"""
{
    module : transactions.py
    desc   : Router API Giao dịch chuẩn hóa theo Hợp đồng API (BA Phần 11).
}
"""

import os
from pathlib import Path
from uuid import UUID, uuid4
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.infrastructure.db.session import get_db
from backend.infrastructure.db.repositories.postgres_transaction_repository import PostgresTransactionRepository
from backend.infrastructure.db.models.orm_models import ModelPredictionORM, TransactionORM
from backend.domain.entities.transaction import TransactionType, TransactionChannel
from backend.services.transaction_service import TransactionService
from backend.services.scoring_service import ScoringService
from backend.ml.inference.risk_engine import RiskEngine
from backend.apps.api.schemas.transaction_schema import TransactionCreateSchema, TransactionResponseSchema
from backend.apps.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["Transactions"])

risk_engine_instance = RiskEngine()

@router.post("/transactions", status_code=status.HTTP_202_ACCEPTED)
def submit_transaction(
    payload: TransactionCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : submit_transaction
        desc   : Gửi giao dịch thanh toán để chấm điểm bất đồng bộ và kiểm tra Idempotency
        input  : payload (TransactionCreateSchema), db (Session)
        output : dict — { message, transaction_id, status }
        loop   : 0 loops
    }
    """
    repo = PostgresTransactionRepository(db)
    service = TransactionService(repo)

    try:
        txn = service.submit_transaction(
            transaction_id=payload.transaction_id,
            account_id=UUID(payload.account_id),
            merchant_id=UUID(payload.merchant_id),
            amount=payload.amount,
            currency=payload.currency,
            transaction_type=TransactionType(payload.transaction_type),
            channel=TransactionChannel(payload.channel),
            device_id=UUID(payload.device_id) if payload.device_id else None,
        )

        scoring_svc = ScoringService(db=db, engine=risk_engine_instance)
        history = service.get_account_history(txn.account_id)
        scoring_svc.score_transaction(txn, history)

        return {
            "message": "Giao dịch đã được chấp nhận xử lý chấm điểm",
            "transaction_id": txn.transaction_id,
            "status": "ACCEPTED",
        }

    except ValueError as e:
        if "Idempotency" in str(e) or "trùng lặp" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

@router.post("/transactions/simulate-paysim")
def simulate_paysim_transactions(
    count: int = 5,
    fraud_only: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : simulate_paysim_transactions
        desc   : Đọc dữ liệu PaySim thực tế, bắn dòng vào AI Engine để kiểm thử độ chính xác so với nhãn gốc
        input  : count (int), fraud_only (bool), db (Session)
        output : dict — kết quả kiểm thử mô hình và độ chính xác thời gian thực
        loop   : 1 loop — duyệt qua các dòng dữ liệu PaySim
    }
    """
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
    sample_path = root / "data" / "features" / "paysim" / "streaming_sample.parquet"
    if not sample_path.exists():
        sample_path = root / "data" / "processed" / "paysim" / "train.parquet"

    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy tập dữ liệu PaySim")

    df = pd.read_parquet(sample_path)
    if fraud_only:
        df = df[df["isFraud"] == 1]
    
    sample_df = df.sample(n=min(count, len(df)), random_state=None)
    scoring_svc = ScoringService(db=db, engine=risk_engine_instance)
    results = []

    # { loop-1: duyệt qua từng bản ghi PaySim, chấm điểm và đánh giá độ chính xác }
    for _, row in sample_df.iterrows():
        txn_id = f"PAYSIM-{uuid4().hex[:8].upper()}"
        amount = float(row.get("amount", 15000000.0))
        is_fraud = int(row.get("isFraud", 0))
        is_transfer = bool(row.get("is_transfer", 1))

        txn_orm = TransactionORM(
            id=str(uuid4()),
            transaction_id=txn_id,
            account_id=f"ACC-PAYSIM-{int(row.get('step', 1)) % 999:03d}",
            merchant_id="MERCH-PAYSIM-VN",
            device_id=str(uuid4()) if is_fraud else "device-known-001",
            amount=amount,
            currency="VND",
            transaction_type="TRANSFER" if is_transfer else "CASH_OUT",
            channel="MOBILE",
            status="SCORED",
        )
        db.add(txn_orm)
        db.commit()

        score_res, shap_res, pred_orm = scoring_svc.score_transaction({
            "id": txn_orm.id,
            "transaction_id": txn_id,
            "account_id": txn_orm.account_id,
            "amount": amount,
            "device_id": txn_orm.device_id,
            "merchant_id": txn_orm.merchant_id,
        })

        is_pred_fraud = score_res.level.value in ["HIGH", "MEDIUM"]
        if is_fraud == 1:
            eval_status = "TRUE_POSITIVE" if is_pred_fraud else "FALSE_NEGATIVE"
        else:
            eval_status = "TRUE_NEGATIVE" if not is_pred_fraud else "FALSE_POSITIVE"

        is_correct = (is_fraud == 1 and is_pred_fraud) or (is_fraud == 0 and not is_pred_fraud)
        top_shap = shap_res[0].get("label") or shap_res[0].get("featureName") if shap_res else "amount"

        results.append({
            "transaction_id": txn_id,
            "amount": amount,
            "channel": txn_orm.transaction_type,
            "risk_score": score_res.value,
            "risk_level": score_res.level.value,
            "is_fraud_label": is_fraud,
            "ground_truth": "GIAN LẬN" if is_fraud == 1 else "HỢP LỆ",
            "evaluation_status": eval_status,
            "is_correct": is_correct,
            "created_case": score_res.level.value in ["HIGH", "MEDIUM"],
            "top_shap_feature": top_shap,
        })

    correct_count = sum(1 for r in results if r["is_correct"])
    accuracy = round((correct_count / len(results)) * 100, 1) if results else 100.0

    return {
        "message": f"Đã mô phỏng và kiểm thử mô hình thành công trên {len(results)} giao dịch PaySim",
        "processed_count": len(results),
        "correct_count": correct_count,
        "accuracy_percentage": accuracy,
        "transactions": results,
    }

@router.get("/transactions/{id}", response_model=TransactionResponseSchema)
def get_transaction_detail(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_transaction_detail
        desc   : Lấy thông tin chi tiết giao dịch cùng kết quả điểm số rủi ro liên quan
        input  : id (str) — transaction_id hoặc khóa chính UUID
        output : TransactionResponseSchema
        loop   : 0 loops
    }
    """
    txn_orm = db.query(TransactionORM).filter(
        (TransactionORM.id == id) | (TransactionORM.transaction_id == id)
    ).first()

    if not txn_orm:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")

    pred_orm = db.query(ModelPredictionORM).filter_by(transaction_id=txn_orm.id).first()

    return TransactionResponseSchema(
        id=txn_orm.id,
        transaction_id=txn_orm.transaction_id,
        account_id=txn_orm.account_id,
        merchant_id=txn_orm.merchant_id,
        amount=txn_orm.amount,
        currency=txn_orm.currency,
        transaction_type=txn_orm.transaction_type,
        channel=txn_orm.channel,
        status=txn_orm.status,
        created_at=txn_orm.created_at,
        scored_at=txn_orm.scored_at,
        risk_score=pred_orm.risk_score if pred_orm else None,
        risk_level=pred_orm.risk_level if pred_orm else None,
        fraud_probability=pred_orm.fraud_probability if pred_orm else None,
        shap_values=pred_orm.shap_values if pred_orm else None,
    )

@router.get("/accounts/{id}/transactions")
@router.get("/transactions/account/{id}")
def get_account_transaction_history(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_account_transaction_history
        desc   : Truy vấn lịch sử giao dịch 30 ngày của tài khoản (US-09)
        input  : id (str) — UUID tài khoản
        output : list[dict] — danh sách các giao dịch trong lịch sử
        loop   : 1 loop — định dạng thông tin giao dịch lịch sử
    }
    """
    repo = PostgresTransactionRepository(db)
    history = repo.find_by_account_id(UUID(id), limit=30)
    # { loop-1: định dạng các đối tượng transaction domain trong lịch sử }
    return [
        {
            "id": str(t.id),
            "transaction_id": t.transaction_id,
            "amount": t.amount,
            "currency": t.currency,
            "channel": t.channel.value,
            "status": t.status.value,
            "created_at": t.created_at.isoformat(),
        }
        for t in history
    ]
