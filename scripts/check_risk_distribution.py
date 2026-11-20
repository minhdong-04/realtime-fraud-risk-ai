"""
{
    script : check_risk_distribution.py
    desc   : Kiem tra ty le phan bo cac muc do rui ro (LOW, MEDIUM, HIGH) trong data thuc te va CSDL
    input  : data/processed, CSDL
    output : In bao cao phan bo
    loop   : 1 loop
    run    : python scripts/check_risk_distribution.py
}
"""

import sys
from collections import Counter
from pathlib import Path
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.infrastructure.db.session import SessionLocal
from backend.infrastructure.db.models.orm_models import TransactionORM, ModelPredictionORM, FraudCaseORM

def main():
    print("\n" + "="*80)
    print("  PHÂN TÍCH TỶ LỆ PHÂN BỐ GIAO DỊCH THỰC TẾ & MỨC ĐỘ RỦI RO (RISK LEVELS)")
    print("="*80)

    # 1. ULB CreditCard
    df_ulb = pd.read_parquet("data/processed/ubl_creditcard/train.parquet")
    ulb_fraud = int((df_ulb["isFraud"] == 1).sum())
    ulb_legit = int((df_ulb["isFraud"] == 0).sum())
    print("\n1. TẬP DỮ LIỆU ULB CREDITCARD (Tổng 170,884 dòng Train):")
    print(f"   - Giao dịch HỢP LỆ (Bình thường / LOW Risk) : {ulb_legit:,} dòng ({ulb_legit/len(df_ulb)*100:.2f}%)")
    print(f"   - Giao dịch GIAN LẬN (Bất thường / HIGH Risk): {ulb_fraud:,} dòng ({ulb_fraud/len(df_ulb)*100:.2f}%)")

    # 2. PaySim
    df_paysim = pd.read_parquet("data/processed/paysim/train.parquet")
    ps_fraud = int((df_paysim["isFraud"] == 1).sum())
    ps_legit = int((df_paysim["isFraud"] == 0).sum())
    print("\n2. TẬP DỮ LIỆU PAYSIM (Tổng 1,662,245 dòng Train):")
    print(f"   - Giao dịch HỢP LỆ (Bình thường / LOW Risk) : {ps_legit:,} dòng ({ps_legit/len(df_paysim)*100:.2f}%)")
    print(f"   - Giao dịch GIAN LẬN (Bất thường / HIGH Risk): {ps_fraud:,} dòng ({ps_fraud/len(df_paysim)*100:.2f}%)")

    # 3. IEEE-CIS
    df_ieee = pd.read_parquet("data/features/ieee_cis/train_features.parquet")
    ieee_fraud = int((df_ieee["isFraud"] == 1).sum())
    ieee_legit = int((df_ieee["isFraud"] == 0).sum())
    print("\n3. TẬP DỮ LIỆU IEEE-CIS (Tổng 354,324 dòng Train):")
    print(f"   - Giao dịch HỢP LỆ (Bình thường / LOW Risk) : {ieee_legit:,} dòng ({ieee_legit/len(df_ieee)*100:.2f}%)")
    print(f"   - Giao dịch GIAN LẬN (Bất thường / HIGH Risk): {ieee_fraud:,} dòng ({ieee_fraud/len(df_ieee)*100:.2f}%)")

    # 4. Cơ sở dữ liệu hiện tại
    db = SessionLocal()
    try:
        preds = db.query(ModelPredictionORM).all()
        cases = db.query(FraudCaseORM).all()
        txns = db.query(TransactionORM).all()

        pred_dist = Counter([p.risk_level for p in preds])
        case_dist = Counter([c.risk_level for c in cases])

        print("\n4. TRONG CƠ SỞ DỮ LIỆU HỆ THỐNG HIỆN TẠI:")
        print(f"   - Tổng số giao dịch đã chấm điểm: {len(txns)} giao dịch")
        print(f"   - Phân bố điểm số AI (ModelPrediction):")
        print(f"     + LOW Risk (Tự động duyệt / STP)  : {pred_dist.get('LOW', 0)} giao dịch")
        print(f"     + MEDIUM Risk (Cần xác thực 2FA)  : {pred_dist.get('MEDIUM', 0)} giao dịch")
        print(f"     + HIGH Risk (Chặn / Mở ca review) : {pred_dist.get('HIGH', 0)} giao dịch")
        print(f"   - Hàng đợi Review của Fraud Analyst (FraudCase):")
        print(f"     + HIGH Risk   : {case_dist.get('HIGH', 0)} ca")
        print(f"     + MEDIUM Risk : {case_dist.get('MEDIUM', 0)} ca")
        print(f"     + LOW Risk    : {case_dist.get('LOW', 0)} ca (Theo nghiệp vụ: LOW tự động duyệt, không mở ca để tránh quá tải Analyst)")
    finally:
        db.close()

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
