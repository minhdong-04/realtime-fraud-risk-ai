"""
{
    script : verify_datasets_integrity.py
    desc   : Kiem tra toan dien tinh toan ven cua du lieu tu Tho (Raw) den Sach (Clean) va Mo hinh (Trained Models)
    input  : data/raw, data/processed, data/features, backend/ml/artifacts
    output : In bao cao chi tiet
    loop   : 1 loop — duyet qua tung tap du lieu
    run    : python scripts/verify_datasets_integrity.py
}
"""

import io
import sys
import json
from pathlib import Path
import pandas as pd

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

def check_file(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "size_mb": 0, "rows": 0, "cols": 0, "nulls": 0}
    size_mb = path.stat().st_size / (1024 * 1024)
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
        return {"exists": True, "size_mb": round(size_mb, 2), "rows": len(df), "cols": df.shape[1], "nulls": int(df.isna().sum().sum())}
    elif path.suffix == ".csv":
        return {"exists": True, "size_mb": round(size_mb, 2), "rows": "CSV File", "cols": "N/A", "nulls": "N/A"}
    return {"exists": True, "size_mb": round(size_mb, 2), "rows": 0, "cols": 0, "nulls": 0}

def main():
    print("\n" + "="*85)
    print("  BÁO CÁO KIỂM ĐỊNH TOÀN DIỆN DỮ LIỆU TỪ THÔ (RAW) ĐẾN SẠCH (CLEAN) & MÔ HÌNH")
    print("="*85)

    datasets = [
        # ULB CreditCard
        ("1. ULB CreditCard - Raw CSV", ROOT / "data/raw/ubl_creditcard/creditcard.csv"),
        ("1. ULB CreditCard - Clean Train", ROOT / "data/processed/ubl_creditcard/train.parquet"),
        ("1. ULB CreditCard - Clean Val", ROOT / "data/processed/ubl_creditcard/val.parquet"),
        ("1. ULB CreditCard - Clean Test", ROOT / "data/processed/ubl_creditcard/test.parquet"),
        
        # IEEE-CIS
        ("2. IEEE-CIS - Raw Train Txn", ROOT / "data/raw/ieee_cis/train_transaction.csv"),
        ("2. IEEE-CIS - Raw Train Identity", ROOT / "data/raw/ieee_cis/train_identity.csv"),
        ("2. IEEE-CIS - Clean Merged Train", ROOT / "data/processed/ieee_cis/train_merged.parquet"),
        ("2. IEEE-CIS - Engineered Train Feats", ROOT / "data/features/ieee_cis/train_features.parquet"),
        ("2. IEEE-CIS - Engineered Test Feats", ROOT / "data/features/ieee_cis/test_features.parquet"),
        
        # PaySim
        ("3. PaySim - Raw CSV", ROOT / "data/raw/paysim/PS_log.csv"),
        ("3. PaySim - Clean Train Parquet", ROOT / "data/processed/paysim/train.parquet"),
        ("3. PaySim - Clean Val Parquet", ROOT / "data/processed/paysim/val.parquet"),
        ("3. PaySim - Clean Test Parquet", ROOT / "data/processed/paysim/test.parquet"),
        ("3. PaySim - Real-time Streaming Sample", ROOT / "data/features/paysim/streaming_sample.parquet"),
    ]

    print(f"{'TẬP DỮ LIỆU / BẢN GHI':<40} | {'TRẠNG THÁI':<10} | {'DUNG LƯỢNG':<10} | {'SỐ DÒNG':<12} | {'SỐ CỘT':<6} | {'NULLS':<6}")
    print("-" * 95)

    # { loop-1: duyet qua tat ca cac file du lieu de kiem tra chat luong }
    for name, path in datasets:
        info = check_file(path)
        status = "[CO SAN]" if info["exists"] else "[CHUA CO]"
        size_str = f"{info['size_mb']:.1f} MB" if info["exists"] else "0 MB"
        rows_str = f"{info['rows']:,}" if isinstance(info["rows"], int) else str(info["rows"])
        cols_str = str(info["cols"])
        nulls_str = str(info["nulls"])
        print(f"{name:<40} | {status:<10} | {size_str:<10} | {rows_str:<12} | {cols_str:<6} | {nulls_str:<6}")

    print("\n" + "="*85)
    print("  KIỂM TRA ARTIFACTS MÔ HÌNH SAU KHI HUẤN LUYỆN (BACKEND ML ARTIFACTS)")
    print("="*85)

    artifacts = [
        ("XGBoost / HistGB Model", ROOT / "backend/ml/artifacts/xgboost_hybrid_v1.0.0.joblib"),
        ("Isolation Forest Anomaly Model", ROOT / "backend/ml/artifacts/isolation_forest_v1.0.0.joblib"),
        ("StandardScaler Transformer", ROOT / "backend/ml/artifacts/scaler.joblib"),
        ("Model Metadata JSON", ROOT / "backend/ml/artifacts/metadata.json"),
    ]

    for name, path in artifacts:
        exists = path.exists()
        size_mb = path.stat().st_size / (1024 * 1024) if exists else 0
        status = "[VALID]" if exists else "[MISSING]"
        print(f"  - {name:<35} : {status} ({size_mb:.2f} MB)")

    if (ROOT / "backend/ml/artifacts/metadata.json").exists():
        with open(ROOT / "backend/ml/artifacts/metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        print("\n  [METRIC TỔNG HỢP]:")
        print(f"    + Mô hình: {meta.get('model_name')} ({meta.get('version')})")
        print(f"    + Tổng số bản ghi đã huấn luyện: {meta.get('total_records_processed'):,} bản ghi")
        print(f"    + PR-AUC: {meta.get('pr_auc')} | ROC-AUC: {meta.get('roc_auc')} | Brier Score: {meta.get('brier_score')}")
        print(f"    + Ngưỡng tối ưu chi phí: {meta.get('optimal_threshold')} (Chi phí tối thiểu: ${meta.get('expected_cost')})")
    
    print("="*85 + "\n")

if __name__ == "__main__":
    main()
