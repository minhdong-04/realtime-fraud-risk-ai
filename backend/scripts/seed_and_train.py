"""
{
    script : seed_and_train.py
    desc   : Script tao du lieu mau (Seed Data) tu tap du lieu PaySim thuc te va tai khoan he thong.
    run    : python backend/scripts/seed_and_train.py
}
"""

import sys
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import random
import pandas as pd

# Bo sung thu muc goc vao sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.core.security import hash_password
from backend.infrastructure.db.session import SessionLocal, init_db
from backend.infrastructure.db.models.orm_models import (
    UserORM, TransactionORM, ModelPredictionORM, FraudCaseORM, ModelVersionORM, AnalystReviewORM
)
from backend.ml.inference.shap_explainer import generate_shap_explanation

def seed_database():
    """
    {
        func   : seed_database
        desc   : Khoi tao CSDL voi tai khoan mac dinh va cac giao dich trich tu bo du lieu PaySim thuc te
        input  : None
        output : None
        loop   : 1 loop — duyet qua cac dong PaySim thuc te de tao giao dich va ca rui ro
    }
    """
    demo_password = os.environ.get("DEMO_PASSWORD")
    if not demo_password:
        sys.exit("[ERROR] Dat bien moi truong DEMO_PASSWORD (mat khau 3 tai khoan demo) truoc khi seed.")
    password_hash = hash_password(demo_password)

    init_db()
    db = SessionLocal()

    try:
        # 1. Tao cac tai khoan nguoi dung mac dinh theo vai tro
        analyst = UserORM(
            id="11111111-1111-1111-1111-111111111111",
            email="analyst@fraud-platform.com",
            hashed_password=password_hash,
            role="ANALYST",
        )
        manager = UserORM(
            id="22222222-2222-2222-2222-222222222222",
            email="manager@fraud-platform.com",
            hashed_password=password_hash,
            role="MANAGER",
        )
        ml_eng = UserORM(
            id="33333333-3333-3333-3333-333333333333",
            email="mlengineer@fraud-platform.com",
            hashed_password=password_hash,
            role="ML_ENGINEER",
        )

        db.merge(analyst)
        db.merge(manager)
        db.merge(ml_eng)
        db.commit()

        # 2. Tao thong tin phien ban mo hinh ML trong registry
        if not db.query(ModelVersionORM).filter_by(version="v1.0.0").first():
            v1 = ModelVersionORM(
                name="xgboost_hybrid",
                version="v1.0.0",
                pr_auc=0.7548,
                recall=0.89,
                precision=0.82,
                f1_score=0.85,
                brier_score=0.0013,
                expected_cost=1463.0,
                status="PRODUCTION",
                is_shadow=False,
            )
            db.add(v1)
        if not db.query(ModelVersionORM).filter_by(version="v1.1.0-candidate").first():
            v2 = ModelVersionORM(
                name="xgboost_hybrid",
                version="v1.1.0-candidate",
                pr_auc=0.7920,
                recall=0.92,
                precision=0.86,
                f1_score=0.89,
                brier_score=0.0008,
                expected_cost=890.0,
                status="CANDIDATE",
                is_shadow=True,
            )
            db.add(v2)
        db.commit()

        # 3. Nap tap du lieu PaySim thuc te de tao du lieu giao dich sinh dong
        sample_path = root_dir / "data" / "features" / "paysim" / "streaming_sample.parquet"
        if not sample_path.exists():
            sample_path = root_dir / "data" / "processed" / "paysim" / "train.parquet"

        if sample_path.exists():
            df_paysim = pd.read_parquet(sample_path).head(40)
        else:
            df_paysim = pd.DataFrame([{"amount": 15000000, "isFraud": 1, "is_transfer": 1, "step": 1}] * 20)

        now = datetime.now(timezone.utc)
        print(f"[INFO] Dang nap {len(df_paysim)} giao dich PaySim vao CSDL...")

        # { loop-1: duyet qua 40 ban ghi PaySim va sinh du lieu ca rui ro }
        for idx, row in df_paysim.iterrows():
            is_fraud = int(row.get("isFraud", 0))
            amount = float(row.get("amount", 25000000.0))
            is_transfer = bool(row.get("is_transfer", 1))
            step = int(row.get("step", 1))

            txn_id = f"PAYSIM-{1000 + idx}"
            created_at = now - timedelta(hours=int(idx) * 2 + random.randint(1, 15))
            
            existing_txn = db.query(TransactionORM).filter_by(transaction_id=txn_id).first()
            if existing_txn:
                txn_pk = existing_txn.id
                existing_txn.amount = amount
                existing_txn.created_at = created_at
                existing_txn.status = "SCORED"
                db.add(existing_txn)
            else:
                txn_pk = str(uuid4())
                txn = TransactionORM(
                    id=txn_pk,
                    transaction_id=txn_id,
                    account_id=f"ACC-PAYSIM-{step % 999:03d}",
                    merchant_id="MERCH-PAYSIM-VN",
                    device_id=str(uuid4()) if is_fraud else "device-known-001",
                    amount=amount,
                    currency="VND",
                    transaction_type="TRANSFER" if is_transfer else "CASH_OUT",
                    channel="MOBILE",
                    status="SCORED",
                    created_at=created_at,
                    scored_at=created_at + timedelta(milliseconds=35),
                )
                db.add(txn)

            db.commit()

            # Phan bo da dang ca HIGH, MEDIUM va LOW
            if idx % 3 == 0 or is_fraud:
                risk_level = "HIGH"
                risk_score = random.randint(78, 98)
            elif idx % 3 == 1:
                risk_level = "MEDIUM"
                risk_score = random.randint(42, 68)
            else:
                risk_level = "LOW"
                risk_score = random.randint(8, 26)

            fraud_proba = round(risk_score / 100.0, 4)

            features_dict = {
                "txn_count_5m": random.randint(4, 8) if risk_level == "HIGH" else (2 if risk_level == "MEDIUM" else 1),
                "txn_count_1h": random.randint(8, 14) if risk_level == "HIGH" else (4 if risk_level == "MEDIUM" else 2),
                "amount_sum_1h": amount * 1.6,
                "unique_merchants_1h": 3 if is_transfer else 1,
                "avg_amount_30d": 3500000.0,
                "amount_ratio": round(amount / 3500000.0, 2),
                "new_device_flag": 1 if risk_level == "HIGH" else 0,
                "new_merchant_flag": 1 if is_transfer else 0,
            }
            shap_values = generate_shap_explanation(features_dict, fraud_proba)

            existing_pred = db.query(ModelPredictionORM).filter_by(transaction_id=txn_pk).first()
            if existing_pred:
                existing_pred.risk_level = risk_level
                existing_pred.risk_score = risk_score
                existing_pred.shap_values = shap_values
                existing_pred.created_at = created_at
                db.add(existing_pred)
            else:
                pred = ModelPredictionORM(
                    transaction_id=txn_pk,
                    model_name="xgboost_hybrid",
                    model_version="v1.0.0",
                    fraud_probability=fraud_proba,
                    anomaly_score=round(fraud_proba * 0.85, 4),
                    risk_score=risk_score,
                    risk_level=risk_level,
                    threshold_used=0.23,
                    shap_values=shap_values,
                    created_at=created_at,
                )
                db.add(pred)

            db.commit()

            # Tao ca rui ro cho ca HIGH, MEDIUM va LOW de Fraud Analyst review
            if risk_level in ["HIGH", "MEDIUM", "LOW"]:
                case_status = "CLOSED" if idx % 4 == 0 else ("ASSIGNED" if idx % 3 == 0 else "OPEN")
                existing_case = db.query(FraudCaseORM).filter_by(transaction_id=txn_pk).first()
                if existing_case:
                    existing_case.risk_level = risk_level
                    existing_case.risk_score = risk_score
                    existing_case.status = case_status
                    existing_case.created_at = created_at
                    db.add(existing_case)
                    case_id = existing_case.id
                else:
                    case_id = str(uuid4())
                    case = FraudCaseORM(
                        id=case_id,
                        transaction_id=txn_pk,
                        risk_level=risk_level,
                        risk_score=risk_score,
                        status=case_status,
                        assigned_to=analyst.id if case_status != "OPEN" else None,
                        created_at=created_at,
                        closed_at=created_at + timedelta(minutes=15) if case_status == "CLOSED" else None,
                    )
                    db.add(case)

                db.commit()

                if case_status == "CLOSED":
                    if not db.query(AnalystReviewORM).filter_by(case_id=case_id).first():
                        review = AnalystReviewORM(
                            case_id=case_id,
                            analyst_id=analyst.id,
                            decision="CONFIRMED_FRAUD" if risk_level == "HIGH" else "STEPPED_UP_APPROVED",
                            reason=f"Phat hien hanh vi chuyen tien bat thuong muc {risk_level} tren tap du lieu PaySim",
                            created_at=created_at + timedelta(minutes=15),
                        )
                        db.add(review)
                        db.commit()

        print("[SUCCESS] Da nap thanh cong du lieu PaySim thuc te voi day du ca HIGH, MEDIUM va LOW.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Loi khoi tao du lieu PaySim: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
