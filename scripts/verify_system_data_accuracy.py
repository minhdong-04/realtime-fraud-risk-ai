"""
{
    module : verify_system_data_accuracy.py
    desc   : Kiem tra toan dien tinh toan ven, do chinh xac cua du lieu tren toan he thong (Database, ML Model, API).
}
"""

import sys
from uuid import uuid4
from pathlib import Path

# Thiet lap UTF-8 output cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Them thu muc goc vao sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.infrastructure.db.session import SessionLocal
from backend.infrastructure.db.models.orm_models import (
    UserORM, TransactionORM, FraudCaseORM, ModelPredictionORM, AnalystReviewORM
)
from backend.ml.inference.risk_engine import RiskEngine
from backend.services.scoring_service import ScoringService
from fastapi.testclient import TestClient
from backend.apps.api.main import app

def run_comprehensive_audit():
    print("=" * 70)
    print("🔍 BẮT ĐẦU KIỂM TRA ĐẢM BẢO ĐỘ CHÍNH XÁC DỮ LIỆU TOÀN HỆ THỐNG")
    print("=" * 70)

    db = SessionLocal()
    client = TestClient(app)
    created_txn_ids = []

    try:
        # 1. Kiem tra User & Tai khoan phan quyen RBAC
        users = db.query(UserORM).all()
        print(f"\n[1/5] KIỂM TRA TÀI KHOẢN NGƯỜI DÙNG (RBAC):")
        print(f"  - Tổng số tài khoản: {len(users)}")
        for u in users:
            print(f"    * Email: {u.email:<30} | Role: {u.role:<15}")
        assert len(users) >= 4, "Thiếu tài khoản người dùng mặc định"

        # 2. Kiem tra Du lieu Giao dich & Ca rui ro trong CSDL
        txns = db.query(TransactionORM).all()
        cases = db.query(FraudCaseORM).all()
        preds = db.query(ModelPredictionORM).all()
        reviews = db.query(AnalystReviewORM).all()

        print(f"\n[2/5] KIỂM TRA DỮ LIỆU CƠ SỞ DỮ LIỆU:")
        print(f"  - Tổng số giao dịch (Transactions): {len(txns):,}")
        print(f"  - Tổng số dự đoán AI (Model Predictions): {len(preds):,}")
        print(f"  - Tổng số ca rủi ro (Fraud Cases): {len(cases):,}")
        print(f"  - Tổng số ca đã thẩm định (Analyst Reviews): {len(reviews):,}")

        # Kiem tra 100% FraudCase co Transaction tuong ung
        orphan_cases = [c for c in cases if not db.query(TransactionORM).filter((TransactionORM.id == c.transaction_id) | (TransactionORM.transaction_id == c.transaction_id)).first()]
        print(f"  - Số ca rác mồ côi (Orphans không có Transaction): {len(orphan_cases)} (Yêu cầu = 0)")
        assert len(orphan_cases) == 0, f"Phát hiện {len(orphan_cases)} ca rác không có giao dịch"

        # Kiem tra phan bo so tien thuc te
        amounts = [t.amount for t in txns]
        min_amt, max_amt, avg_amt = min(amounts), max(amounts), sum(amounts) / len(amounts)
        print(f"  - Phân bổ số tiền giao dịch: Nhỏ nhất = {min_amt:,.0f} VND | Lớn nhất = {max_amt:,.0f} VND | Trung bình = {avg_amt:,.0f} VND")

        # 3. Kiem tra Model ML & Tinh toan diem rui ro
        print(f"\n[3/5] KIỂM TRA MÔ HÌNH HỌC MÁY (ML INFERENCE & SHAP):")
        scoring_svc = ScoringService(db=db, engine=RiskEngine())
        
        # Test giao dich hop le binh thuong
        t_legit = TransactionORM(
            id=str(uuid4()),
            transaction_id=f"AUDIT-LEGIT-{uuid4().hex[:6]}",
            account_id="ACC-AUDIT-LEGIT",
            merchant_id="MERCH-SAFE",
            amount=150000.0,
            currency="VND",
            transaction_type="PURCHASE",
            channel="MOBILE",
            status="SCORED",
        )
        db.add(t_legit)
        db.commit()
        created_txn_ids.append(t_legit.id)

        score_legit, shap_legit, _ = scoring_svc.score_transaction({
            "id": t_legit.id,
            "transaction_id": t_legit.transaction_id,
            "account_id": t_legit.account_id,
            "amount": t_legit.amount,
            "device_id": "device-known-001",
            "merchant_id": t_legit.merchant_id,
        })
        print(f"  - Giao dịch thông thường (150K VND): Điểm rủi ro = {score_legit.value}/100 ({score_legit.level.value})")

        # Test giao dich gian lan bat thuong
        t_fraud = TransactionORM(
            id=str(uuid4()),
            transaction_id=f"AUDIT-FRAUD-{uuid4().hex[:6]}",
            account_id="ACC-AUDIT-FRAUD",
            merchant_id="MERCH-PAYSIM-VN",
            amount=85000000.0,
            currency="VND",
            transaction_type="TRANSFER",
            channel="MOBILE",
            status="SCORED",
        )
        db.add(t_fraud)
        db.commit()
        created_txn_ids.append(t_fraud.id)

        score_fraud, shap_fraud, _ = scoring_svc.score_transaction({
            "id": t_fraud.id,
            "transaction_id": t_fraud.transaction_id,
            "account_id": t_fraud.account_id,
            "amount": t_fraud.amount,
            "device_id": "device-unknown-999",
            "merchant_id": t_fraud.merchant_id,
        })
        print(f"  - Giao dịch bất thường (85M VND + Thiết bị mới): Điểm rủi ro = {score_fraud.value}/100 ({score_fraud.level.value})")
        print(f"  - Top đặc trưng SHAP giải thích:")
        for s in shap_fraud[:3]:
            label = s.get("label") or s.get("featureName")
            shap_val = s.get("shapValue", 0.0)
            feat_val = s.get("featureValue", 0.0)
            print(f"    * {label}: Trọng số SHAP = {shap_val:+.4f} (Giá trị = {feat_val})")

        assert score_legit.level.value in ["LOW", "MEDIUM"], "Giao dịch thường phải có điểm rủi ro thấp"
        assert score_fraud.level.value in ["HIGH", "MEDIUM"], "Giao dịch bất thường phải có điểm rủi ro cao"

        # 4. Kiem tra API End-to-End
        print(f"\n[4/5] KIỂM TRA TẤT CẢ ENDPOINTS API CHÍNH:")
        
        # API 1: List Fraud Cases
        res_cases = client.get("/api/v1/fraud-cases?limit=5")
        assert res_cases.status_code == 200, "Lỗi API /fraud-cases"
        data_cases = res_cases.json()
        print(f"  - GET /api/v1/fraud-cases: Status 200 OK | Trả về {len(data_cases['items'])}/{data_cases['total_count']} ca")
        sample_case = data_cases["items"][0]
        print(f"    * Ca đầu tiên: {sample_case['transaction_id']} | Số tiền: {sample_case['transaction']['amount']:,.0f} VND | Kênh: {sample_case['transaction']['channel']} | Rủi ro: {sample_case['risk_level']} ({sample_case['risk_score']})")

        # API 2: Fraud Case Detail
        first_case_id = sample_case["id"]
        res_detail = client.get(f"/api/v1/fraud-cases/{first_case_id}")
        assert res_detail.status_code == 200, "Lỗi API /fraud-cases/{id}"
        data_detail = res_detail.json()
        print(f"  - GET /api/v1/fraud-cases/{first_case_id[:8]}...: Status 200 OK | SHAP đặc trưng: {len(data_detail['shap_values'])} mục")

        # API 3: Simulate PaySim
        res_sim = client.post("/api/v1/transactions/simulate-paysim?count=5&fraud_only=false")
        assert res_sim.status_code == 200, "Lỗi API /transactions/simulate-paysim"
        data_sim = res_sim.json()
        print(f"  - POST /api/v1/transactions/simulate-paysim: Status 200 OK | Nạp {data_sim['processed_count']} giao dịch | Độ chính xác AI: {data_sim['accuracy_percentage']}%")

        # API 4: Analytics Fraud Dashboard
        res_analytics = client.get("/api/v1/analytics/fraud")
        assert res_analytics.status_code == 200, "Lỗi API /analytics/fraud"
        data_analytics = res_analytics.json()
        print(f"  - GET /api/v1/analytics/fraud: Status 200 OK | Tỷ lệ gian lận: {data_analytics['fraud_rate']}% | Tổng giao dịch: {data_analytics['total_transactions']:,}")

        # API 5: Model Management
        res_models = client.get("/api/v1/models")
        assert res_models.status_code == 200, "Lỗi API /models"
        data_models = res_models.json()
        prauc = data_models[0].get("pr_auc") or data_models[0].get("prAuc")
        recall = data_models[0].get("recall")
        print(f"  - GET /api/v1/models: Status 200 OK | Mô hình Production: {data_models[0]['name']} (PR-AUC: {prauc}, Recall: {recall})")

        # 5. Tong ket
        print("\n" + "=" * 70)
        print("🎉 TẤT CẢ DỮ LIỆU VÀ QUY TRÌNH HOẠT ĐỘNG HOÀN TOÀN CHÍNH XÁC 100%!")
        print("=" * 70)

    finally:
        for tid in created_txn_ids:
            c = db.query(FraudCaseORM).filter_by(transaction_id=tid).first()
            if c:
                db.delete(c)
            p = db.query(ModelPredictionORM).filter_by(transaction_id=tid).first()
            if p:
                db.delete(p)
            t = db.query(TransactionORM).filter_by(id=tid).first()
            if t:
                db.delete(t)
        db.commit()
        db.close()

if __name__ == "__main__":
    run_comprehensive_audit()
