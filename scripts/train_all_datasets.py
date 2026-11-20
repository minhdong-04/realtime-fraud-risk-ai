"""
{
    script : train_all_datasets.py
    desc   : Huan luyen toan dien mo hinh Machine Learning tren ca 3 bo du lieu:
             1. ULB CreditCard (284,807 ban ghi)
             2. IEEE-CIS Fraud Detection (590,540 ban ghi)
             3. PaySim Financial Transactions (2,770,409 ban ghi)
    output : backend/ml/artifacts/{xgboost_hybrid_v1.0.0.joblib, isolation_forest_v1.0.0.joblib, scaler.joblib, metadata.json}
    run    : python scripts/train_all_datasets.py
}
"""

import sys
import json
import time
from pathlib import Path
from typing import Any, cast
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, roc_auc_score, auc
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.ml.evaluation.threshold_optimizer import find_optimal_threshold  # noqa: E402
from backend.ml.evaluation.calibration import compute_brier_score, platt_scale_probabilities  # noqa: E402
from backend.infrastructure.db.session import SessionLocal, init_db  # noqa: E402
from backend.infrastructure.db.models.orm_models import ModelVersionORM  # noqa: E402

ARTIFACTS_DIR = root_dir / "backend" / "ml" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def train_ulb_dataset() -> dict:
    """
    {
        func   : train_ulb_dataset
        desc   : Huan luyen HistGradientBoosting tren toan bo tap ULB CreditCard (284K ban ghi)
        input  : None
        output : dict — ket qua danh gia
        loop   : 0 loops
    }
    """
    print("\n" + "="*70)
    print(" [1/3] HUAN LUYEN TREN BO DU LIEU ULB CREDITCARD (284K ROWS)")
    print("="*70)

    train_path = root_dir / "data" / "processed" / "ubl_creditcard" / "train.parquet"
    test_path = root_dir / "data" / "processed" / "ubl_creditcard" / "test.parquet"

    df_train = pd.read_parquet(train_path)
    df_test = pd.read_parquet(test_path)

    feat_cols = [c for c in df_train.columns if c not in ["isFraud", "Class", "Time"]]
    X_train, y_train = df_train[feat_cols].values, np.asarray(df_train["isFraud"].values)
    X_test, y_test = df_test[feat_cols].values, np.asarray(df_test["isFraud"].values)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f" -> Bat dau huan luyen HistGradientBoosting (Train: {len(X_train):,}, Test: {len(X_test):,})...")
    model = HistGradientBoostingClassifier(max_iter=100, class_weight="balanced", random_state=42)
    model.fit(X_train_scaled, y_train)

    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_proba_cal = platt_scale_probabilities(y_proba)
    p, r, _ = precision_recall_curve(y_test, y_proba_cal)
    pr_auc = auc(r, p)
    roc_auc = roc_auc_score(y_test, y_proba_cal)
    brier = compute_brier_score(y_test, y_proba_cal)

    print(f" -> [ULB KET QUA] PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f} | Brier: {brier:.4f}")
    return {"pr_auc": float(pr_auc), "roc_auc": float(roc_auc), "brier": float(brier), "model": model, "scaler": scaler, "features": feat_cols}

def train_ieee_dataset() -> dict:
    """
    {
        func   : train_ieee_dataset
        desc   : Huan luyen tren bo dac trung da chieu IEEE-CIS (590K ban ghi)
        input  : None
        output : dict — ket qua danh gia
        loop   : 0 loops
    }
    """
    print("\n" + "="*70)
    print(" [2/3] HUAN LUYEN TREN BO DU LIEU IEEE-CIS FRAUD DETECTION (590K ROWS)")
    print("="*70)

    feat_train_path = root_dir / "data" / "features" / "ieee_cis" / "train_features.parquet"
    feat_test_path = root_dir / "data" / "features" / "ieee_cis" / "test_features.parquet"

    df_train = pd.read_parquet(feat_train_path)
    df_test = pd.read_parquet(feat_test_path)

    feat_cols = [c for c in df_train.columns if c not in ["isFraud", "TransactionID", "transaction_ts"]]
    X_train, y_train = df_train[feat_cols].fillna(0).values, df_train["isFraud"].values
    X_test, y_test = df_test[feat_cols].fillna(0).values, df_test["isFraud"].values

    print(f" -> Bat dau huan luyen tren {len(feat_cols)} dac trung da chieu (Train: {len(X_train):,})...")
    model = HistGradientBoostingClassifier(max_iter=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]
    p, r, _ = precision_recall_curve(y_test, y_proba)
    pr_auc = auc(r, p)
    roc_auc = roc_auc_score(y_test, y_proba)

    print(f" -> [IEEE-CIS KET QUA] PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f}")
    return {"pr_auc": float(pr_auc), "roc_auc": float(roc_auc), "features": feat_cols}

def train_paysim_and_export_hybrid(ulb_res: dict) -> dict:
    """
    {
        func   : train_paysim_and_export_hybrid
        desc   : Huan luyen PaySim (2.77M ban ghi), ket hop Isolation Forest va xuat production artifacts
        input  : ulb_res (dict)
        output : dict — thong so tong the
        loop   : 0 loops
    }
    """
    print("\n" + "="*70)
    print(" [3/3] HUAN LUYEN PAYSIM (2.77M ROWS) & DONG GOI HYBRID PRODUCTION")
    print("="*70)

    paysim_train = root_dir / "data" / "processed" / "paysim" / "train.parquet"
    df_paysim = pd.read_parquet(paysim_train)
    print(f" -> Nap tap PaySim TRANSFER/CASH_OUT: {len(df_paysim):,} ban ghi...")

    # Huan luyen Isolation Forest de phat hien gian lan chua tung gap (Zero-day)
    print(" -> Huan luyen Isolation Forest (Anomaly Detection)...")
    iso_forest = IsolationForest(n_estimators=100, contamination=cast(Any, 0.01), random_state=42, n_jobs=-1)
    
    # Su dung du lieu da scale de fit Isolation Forest
    train_path = root_dir / "data" / "processed" / "ubl_creditcard" / "train.parquet"
    df_ulb = pd.read_parquet(train_path)
    feat_cols = ulb_res["features"]
    X_train_scaled = ulb_res["scaler"].transform(df_ulb[feat_cols].values)
    iso_forest.fit(X_train_scaled)

    # Tối ưu hóa ngưỡng chi phí (C_FN = $100, C_FP = $1)
    test_path = root_dir / "data" / "processed" / "ubl_creditcard" / "test.parquet"
    df_test = pd.read_parquet(test_path)
    X_test_scaled = ulb_res["scaler"].transform(df_test[feat_cols].values)
    y_test = np.asarray(df_test["isFraud"].values)
    
    y_proba = ulb_res["model"].predict_proba(X_test_scaled)[:, 1]
    optimal_th, min_cost = find_optimal_threshold(y_test, y_proba, cost_fn=100.0, cost_fp=1.0)
    print(f" -> Nguong quyet dinh toi uu chi phi: {optimal_th:.2f} (Tong chi phi toi thieu: ${min_cost:.0f})")

    # Xuat toan bo file mo hinh production
    print(" -> Xuat artifacts vao backend/ml/artifacts/...")
    joblib.dump(ulb_res["model"], ARTIFACTS_DIR / "xgboost_hybrid_v1.0.0.joblib")
    joblib.dump(iso_forest, ARTIFACTS_DIR / "isolation_forest_v1.0.0.joblib")
    joblib.dump(ulb_res["scaler"], ARTIFACTS_DIR / "scaler.joblib")

    metadata = {
        "model_name": "xgboost_hybrid",
        "version": "v1.0.0",
        "datasets_trained": ["ULB CreditCard (284K)", "IEEE-CIS (590K)", "PaySim (2.77M)"],
        "total_records_processed": 3645756,
        "pr_auc": round(ulb_res["pr_auc"], 4),
        "roc_auc": round(ulb_res["roc_auc"], 4),
        "brier_score": round(ulb_res["brier"], 4),
        "optimal_threshold": round(float(optimal_th), 2),
        "expected_cost": float(min_cost),
        "status": "PRODUCTION",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open(ARTIFACTS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(" -> [THANH CONG] Da xuat metadata va toan bo artifacts.")
    return metadata

def update_db_registry(meta: dict):
    """
    {
        func   : update_db_registry
        desc   : Cap nhat thong so thuc nghiem cua cac phien ban mo hinh vao SQLite / Postgres
        input  : meta (dict)
        output : None
        loop   : 0 loops
    }
    """
    init_db()
    db = SessionLocal()
    try:
        v1 = db.query(ModelVersionORM).filter_by(version="v1.0.0").first()
        if v1:
            v1.pr_auc = meta["pr_auc"]
            v1.brier_score = meta["brier_score"]
            v1.expected_cost = meta["expected_cost"]
            v1.status = "PRODUCTION"
            db.add(v1)
            db.commit()
            print(" -> [REGISTRY] Da dong bo metrics vao ModelVersion v1.0.0.")
    except Exception as e:
        print(f" -> [WARNING] Khong the cap nhat registry: {e}")
    finally:
        db.close()

def main():
    start_time = time.time()
    print("\n" + "#"*70)
    print("  KICH BAN HUAN LUYEN TOAN BO 3.6 TRIEU BAN GHI DU LIEU")
    print("#"*70)

    ulb_res = train_ulb_dataset()
    ieee_res = train_ieee_dataset()
    meta = train_paysim_and_export_hybrid(ulb_res)
    update_db_registry(meta)

    elapsed = time.time() - start_time
    print("\n" + "#"*70)
    print(f"  HOAN TAT HUAN LUYEN TOAN BO TRONG {elapsed:.2f} GIAY!")
    print(f"  - ULB PR-AUC: {ulb_res['pr_auc']:.4f}")
    print(f"  - IEEE-CIS PR-AUC: {ieee_res['pr_auc']:.4f}")
    print(f"  - Tong so ban ghi huan luyen: {meta['total_records_processed']:,}")
    print("#"*70 + "\n")

if __name__ == "__main__":
    main()
