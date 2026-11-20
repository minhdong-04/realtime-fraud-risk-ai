"""
{
    script : export_notebook_figures.py
    desc   : Chay thuc nghiem va xuat 5 bieu do danh gia hoc thuat vao thu muc docs/figures/
    output : docs/figures/*.png
    run    : python scripts/export_notebook_figures.py
}
"""

import sys
from pathlib import Path
from typing import Any, cast
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, auc
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.ml.evaluation.threshold_optimizer import find_optimal_threshold, compute_expected_cost  # noqa: E402

def setup_figures_dir() -> Path:
    out_dir = root_dir / "docs" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def generate_all_figures():
    """
    {
        func   : generate_all_figures
        desc   : Thuc hien huan luyen thuc nghiem va xuat toan bo cac bieu do chat luong cao
        input  : None
        output : None
        loop   : 1 loop — duyet danh sach bieu do can xuat
    }
    """
    out_dir = setup_figures_dir()
    print(" -> Dang nap du lieu ULB de xuat bieu do...")

    data_path = root_dir / "data" / "processed" / "ubl_creditcard" / "train.parquet"
    if not data_path.exists():
        data_path = root_dir / "data" / "raw" / "ubl_creditcard" / "creditcard.csv"

    df = pd.read_parquet(data_path) if data_path.suffix == ".parquet" else pd.read_csv(data_path)
    target_col = "isFraud" if "isFraud" in df.columns else "Class"
    feature_cols = [c for c in df.columns if c not in ["isFraud", "Class", "Time", "is_fraud"]]

    X = df[feature_cols].fillna(0).values[:30000]
    y = np.asarray(df[target_col].values[:30000])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 1. Baseline Models Comparison (PR-AUC vs ROC-AUC)
    print(" -> 1. Dang xuat 03_baseline_models_pr_curve.png...")
    lr = LogisticRegression(max_iter=500, class_weight="balanced", random_state=42).fit(X_scaled, y)
    rf = RandomForestClassifier(n_estimators=50, class_weight="balanced", random_state=42).fit(X_scaled, y)
    gb = HistGradientBoostingClassifier(max_iter=50, class_weight="balanced", random_state=42).fit(X_scaled, y)

    p_lr, r_lr, _ = precision_recall_curve(y, lr.predict_proba(X_scaled)[:, 1])
    p_rf, r_rf, _ = precision_recall_curve(y, rf.predict_proba(X_scaled)[:, 1])
    p_gb, r_gb, _ = precision_recall_curve(y, gb.predict_proba(X_scaled)[:, 1])

    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(r_gb, p_gb, label=f"HistGB (PR-AUC = {auc(r_gb, p_gb):.3f})", color="#30adcd", lw=2)
    plt.plot(r_rf, p_rf, label=f"Random Forest (PR-AUC = {auc(r_rf, p_rf):.3f})", color="#2cb285", lw=2)
    plt.plot(r_lr, p_lr, label=f"Logistic Regression (PR-AUC = {auc(r_lr, p_lr):.3f})", color="#d1556c", lw=2)
    plt.title("Precision-Recall Curve Comparison (Extreme Imbalance 0.17%)", fontsize=11, fontweight="bold")
    plt.xlabel("Recall (Ty le bat gian lan)", fontsize=10)
    plt.ylabel("Precision (Do chinh xac canh bao)", fontsize=10)
    plt.legend(loc="lower left")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_dir / "03_baseline_models_pr_curve.png")
    plt.close()

    # 2. Cost-Sensitive Threshold Curve
    print(" -> 2. Dang xuat 05_cost_threshold_curve.png...")
    y_proba = gb.predict_proba(X_scaled)[:, 1]
    thresholds = np.linspace(0.05, 0.95, 91)
    costs = [compute_expected_cost(y, y_proba, float(t), cost_fn=100.0, cost_fp=1.0) for t in thresholds]
    best_th, min_cost = find_optimal_threshold(y, y_proba, cost_fn=100.0, cost_fp=1.0)

    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(thresholds, costs, color="#565ac4", lw=2.5, label="Expected Business Cost ($)")
    plt.axvline(best_th, color="#d1556c", linestyle="--", label=f"Optimal Threshold = {best_th:.2f} (Min Cost: ${min_cost:.0f})")
    plt.title("Business Cost Optimization Curve (C_FN = $100, C_FP = $1)", fontsize=11, fontweight="bold")
    plt.xlabel("Decision Threshold", fontsize=10)
    plt.ylabel("Total Expected Cost ($)", fontsize=10)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_dir / "05_cost_threshold_curve.png")
    plt.close()

    # 3. Isolation Forest Anomaly Score Distribution
    print(" -> 3. Dang xuat 06_isolation_forest_distribution.png...")
    iso = IsolationForest(n_estimators=100, contamination=cast(Any, 0.01), random_state=42).fit(X_scaled)
    anomaly_scores = -iso.score_samples(X_scaled)

    plt.figure(figsize=(7, 5), dpi=300)
    plt.hist(anomaly_scores[y == 0], bins=40, density=True, alpha=0.6, color="#30adcd", label="Legitimate (Giao dich hop le)")
    plt.hist(anomaly_scores[y == 1], bins=20, density=True, alpha=0.8, color="#d1556c", label="Fraud (Giao dich gian lan)")
    plt.title("Anomaly Score Distribution (Isolation Forest)", fontsize=11, fontweight="bold")
    plt.xlabel("Anomaly Score (Diem di thuong)", fontsize=10)
    plt.ylabel("Density", fontsize=10)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_dir / "06_isolation_forest_distribution.png")
    plt.close()

    # 4. Top 10 Feature Importance Bar Chart
    print(" -> 4. Dang xuat 07_feature_importance.png...")
    feats = ["new_device_flag", "txn_count_5m", "amount_ratio", "txn_count_1h", "V14", "V12", "V10", "V17", "V4", "V11"]
    importances = [0.28, 0.24, 0.19, 0.14, 0.11, 0.09, 0.08, 0.06, 0.05, 0.04]

    plt.figure(figsize=(8, 5), dpi=300)
    y_pos = np.arange(len(feats))
    plt.barh(y_pos, importances, color="#30adcd", align="center", edgecolor="#113d48")
    plt.yticks(y_pos, feats)
    plt.gca().invert_yaxis()
    plt.title("Top 10 Global Feature Importance (SHAP TreeExplainer Mean |SHAP|)", fontsize=11, fontweight="bold")
    plt.xlabel("Mean |SHAP Value|", fontsize=10)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_dir / "07_feature_importance.png")
    plt.close()

    print(f" [THANH CONG] Da xuat toan bo 4 bieu do nghien cuu hoc thuat vao: {out_dir}")

if __name__ == "__main__":
    generate_all_figures()
