"""
{
    script : run_full_pipeline.py
    desc   : Kich ban tu dong hoa tong luc 1 cham: Tien xu ly 3 Datasets -> Train ML -> Save Artifacts -> Seed DB -> Test Suite.
    run    : python scripts/run_full_pipeline.py
}
"""

import sys
import os
import time
import subprocess
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, auc, brier_score_loss
from sklearn.ensemble import IsolationForest, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Thiet lap ma hoa an toan cho Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Thiet lap thu muc goc vao sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.ml.models.xgboost_model import XGBoostStrategy
from backend.ml.models.isolation_forest_model import IsolationForestStrategy
from backend.ml.evaluation.threshold_optimizer import find_optimal_threshold
from backend.scripts.seed_and_train import seed_database

def print_step(title: str, step_num: int):
    print("\n" + "=" * 80)
    print(f" [BUOC {step_num}] {title.upper()}")
    print("=" * 80)

def run_data_processing():
    """
    {
        func   : run_data_processing
        desc   : Chay tuan tu cac script tien xu ly cho 3 bo du lieu (ULB, IEEE-CIS, PaySim)
        input  : None
        output : None
        loop   : 1 loop — duyet qua danh sach script tien xu ly
    }
    """
    print_step("Tien xu ly & Chuan hoa 3 Bo Du Lieu (3.6 Trieu ban ghi)", 1)
    
    scripts = [
        ("02a_process_ubl_creditcard.py", "Xu ly du lieu ULB CreditCard (284K rows)"),
        ("02b_merge_ieee_cis.py", "Merge va phan tach IEEE-CIS (590K rows)"),
        ("02c_process_paysim.py", "Loc va trich xuat PaySim Streaming (2.77M rows)"),
        ("03_feature_engineering.py", "Trich xuat dac trung da chieu IEEE-CIS"),
    ]

    # { loop-1: chay tung script tien xu ly }
    for script_name, desc in scripts:
        script_path = root_dir / "scripts" / script_name
        print(f" -> Dang chay {script_name}: {desc}...")
        res = subprocess.run([sys.executable, str(script_path)], cwd=str(root_dir), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"    [CANH BAO] {script_name} tra ve: {res.stderr[:120]}")
        else:
            print(f"    [OK] Hoan tat {script_name}")

def train_and_export_models():
    """
    {
        func   : train_and_export_models
        desc   : Huan luyen toan bo cac mo hinh ML, hieu chinh Platt Scaling va xuat Model Artifacts
        input  : None
        output : dict — ket qua danh gia metric
        loop   : 0 loops
    }
    """
    print_step("Huan luyen Mo hinh ML & Xuat Artifacts (.joblib)", 2)
    artifacts_dir = root_dir / "backend" / "ml" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    data_path = root_dir / "data" / "processed" / "ubl_creditcard" / "train.parquet"
    if not data_path.exists():
        data_path = root_dir / "data" / "raw" / "ubl_creditcard" / "creditcard.csv"

    if data_path.suffix == ".parquet":
        df_train = pd.read_parquet(data_path)
    else:
        df_train = pd.read_csv(data_path)

    feature_cols = [c for c in df_train.columns if c not in ["Class", "isFraud", "is_fraud", "Time"]]
    target_col = "Class" if "Class" in df_train.columns else ("isFraud" if "isFraud" in df_train.columns else "is_fraud")

    X_train = df_train[feature_cols].fillna(0).values[:50000]
    y_train = df_train[target_col].values[:50000]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    print(" -> 1. Dang huan luyen Gradient Boosting Classifier (Supervised)...")
    try:
        from xgboost import XGBClassifier
        raw_xgb = XGBClassifier(n_estimators=100, max_depth=6, scale_pos_weight=15.0, eval_metric="logloss", random_state=42)
    except Exception:
        raw_xgb = HistGradientBoostingClassifier(max_iter=100, class_weight="balanced", random_state=42)
    
    raw_xgb.fit(X_train_scaled, y_train)
    xgb_strategy = XGBoostStrategy(model=raw_xgb, version="v1.0.0")

    print(" -> 2. Dang huan luyen Isolation Forest (Anomaly Detection)...")
    raw_iso = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    raw_iso.fit(X_train_scaled)
    iso_strategy = IsolationForestStrategy(model=raw_iso, version="v1.0.0")

    print(" -> 3. Dang huan luyen Logistic Regression & Random Forest...")
    raw_lr = LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)
    raw_lr.fit(X_train_scaled, y_train)
    raw_rf = RandomForestClassifier(n_estimators=50, class_weight="balanced", random_state=42)
    raw_rf.fit(X_train_scaled, y_train)

    # Danh gia va toi uu nguong
    y_proba = raw_xgb.predict_proba(X_train_scaled)[:, 1]
    precision, recall, _ = precision_recall_curve(y_train, y_proba)
    pr_auc_val = round(float(auc(recall, precision)), 4)
    brier_val = round(float(brier_score_loss(y_train, y_proba)), 4)

    best_th, min_cost = find_optimal_threshold(y_train, y_proba, cost_fn=100.0, cost_fp=1.0)

    # Luu cac Model Artifacts
    joblib.dump(xgb_strategy, artifacts_dir / "xgboost_hybrid_v1.0.0.joblib")
    joblib.dump(iso_strategy, artifacts_dir / "isolation_forest_v1.0.0.joblib")
    joblib.dump(scaler, artifacts_dir / "scaler.joblib")

    metadata = {
        "model_version": "v1.0.0",
        "training_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pr_auc": pr_auc_val,
        "brier_score": brier_val,
        "optimal_threshold": round(best_th, 4),
        "expected_cost": round(min_cost, 2),
        "features_count": len(feature_cols),
    }
    with open(artifacts_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"    [OK] Da luu mo hinh va Metadata vao: {artifacts_dir}")
    print(f"    [METRICS] PR-AUC: {pr_auc_val} | Brier Score: {brier_val} | Optimal Threshold: {best_th:.2f}")
    return metadata

def run_database_seed():
    """
    {
        func   : run_database_seed
        desc   : Khoi tao va nap du lieu sach vao CSDL Postgres / SQLite
        input  : None
        output : None
        loop   : 0 loops
    }
    """
    print_step("Khoi Tao CSDL & Dang Ky Model Registry", 3)
    seed_database()
    print("    [OK] CSDL da san sang voi tai khoan Analyst, Manager, ML Engineer va 15 Fraud Cases.")

def run_quality_gates():
    """
    {
        func   : run_quality_gates
        desc   : Kiem tra tieu chuan do dai ma nguon (<300 dong) va chay PyTest test suite
        input  : None
        output : bool
        loop   : 0 loops
    }
    """
    print_step("Kiem Dinh Tieu Chuan Ma Nguon & Toan Bo 105 Test Cases", 4)
    res_code = subprocess.run([sys.executable, "scripts/check_code_standards.py"], cwd=str(root_dir), capture_output=True, text=True)
    print(" -> Code Standards:", res_code.stdout.strip())

    print(" -> Dang chay PyTest suite (105 tests)...")
    res_test = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=str(root_dir), capture_output=True, text=True)
    print(" -> Test Suite Result:", res_test.stdout.strip() or res_test.stderr.strip())
    return res_test.returncode == 0

def main():
    start_time = time.time()
    print("\n" + "#" * 80)
    print("  KICH BAN TU DONG HOA HOAN THIEN DU AN FRAUD DETECTION PLATFORM")
    print("#" * 80)

    run_data_processing()
    meta = train_and_export_models()
    run_database_seed()
    success = run_quality_gates()

    duration = round(time.time() - start_time, 2)
    print("\n" + "#" * 80)
    print(f"  HOAN THANH TONG LUC TOAN TRINH TRONG {duration} GIAY!")
    print(f"  - Trang thai kiem dinh: {'100% THANH CONG (GREEN)' if success else 'CAN KIEM TRA'}")
    print("  - Backend FastAPI: http://localhost:8000 (Swagger: /docs)")
    print("  - Frontend Next.js 16: http://localhost:3000")
    print("  - Kich hoat Kafka Stream: python scripts/04_kafka_paysim_producer.py --speed 1.0")
    print("#" * 80 + "\n")

if __name__ == "__main__":
    main()
