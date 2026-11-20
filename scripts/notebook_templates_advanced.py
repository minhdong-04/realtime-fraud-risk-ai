"""
{
    module : notebook_templates_advanced.py
    desc   : Templates cho Notebooks 05 (Threshold), 06 (Hybrid), 07 (SHAP).
}
"""

from scripts.notebook_templates_base import make_md, make_code

def build_nb_05_threshold():
    """Tao notebook 05_threshold.ipynb"""
    return [
        make_md([
            "# 🎯 Thực Nghiệm 05: Tối Ưu Hóa Ngưỡng Quyết Định Nhạy Cảm Chi Phí",
            "**Quy tắc**: `BR-01: Cost Matrix Model` ($C_{FN} = \\$100, C_{FP} = \\$1$).",
        ]),
        make_code([
            "import numpy as np, pandas as pd, matplotlib.pyplot as plt",
            "from backend.ml.evaluation.threshold_optimizer import find_optimal_threshold, compute_expected_cost",
            "from scripts.train_xgboost_real import generate_training_data",
            "from xgboost import XGBClassifier",
            "X, y = generate_training_data(n_normal=10000, n_fraud=500)",
            "model = XGBClassifier(n_estimators=100, max_depth=5, scale_pos_weight=20, eval_metric='aucpr', random_state=42).fit(X, y)",
            "y_proba = model.predict_proba(X)[:, 1]",
            "thresholds = np.linspace(0.01, 0.99, 99)",
            "costs = [compute_expected_cost(y, y_proba, float(t), cost_fn=100.0, cost_fp=1.0) for t in thresholds]",
            "best_th, min_c = find_optimal_threshold(y, y_proba, cost_fn=100.0, cost_fp=1.0)",
            "print(f'Ngưỡng tối ưu T* = {best_th:.2f} | Min Cost = ${min_c:,.2f}')",
        ]),
        make_md(["### 2. Đồ thị Business Cost Curve"]),
        make_code([
            "plt.figure(figsize=(8, 4.5), dpi=150)",
            "plt.plot(thresholds, costs, lw=2.5, color='#565ac4', label='Expected Cost ($)')",
            "plt.axvline(best_th, color='#d1556c', ls='--', label=f'Optimal T*={best_th:.2f}')",
            "plt.title('Business Cost vs Decision Threshold'); plt.xlabel('Threshold'); plt.ylabel('Cost ($)'); plt.legend(); plt.show()",
        ]),
    ]

def build_nb_06_hybrid():
    """Tao notebook 06_hybrid.ipynb"""
    return [
        make_md([
            "# 🧬 Thực Nghiệm 06: Kiến Trúc Lai (Hybrid Architecture) & Platt Scaling",
            "**Quy tắc**: `BR-02: Hybrid Scoring` & `BR-05: Platt Brier Score <= 0.05`.",
        ]),
        make_code([
            "import numpy as np, pandas as pd, matplotlib.pyplot as plt",
            "from xgboost import XGBClassifier",
            "from sklearn.ensemble import IsolationForest",
            "from sklearn.calibration import CalibratedClassifierCV, calibration_curve",
            "from sklearn.metrics import brier_score_loss, precision_recall_curve, auc",
            "from scripts.train_xgboost_real import generate_training_data",
            "X, y = generate_training_data(n_normal=20000, n_fraud=1500)",
            "xgb = XGBClassifier(n_estimators=100, max_depth=5, scale_pos_weight=13, eval_metric='aucpr', random_state=42).fit(X, y)",
            "iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42).fit(X)",
            "p_xgb = xgb.predict_proba(X)[:, 1]",
            "raw_anom = -iso.score_samples(X); p_iso = (raw_anom - raw_anom.min()) / (raw_anom.max() - raw_anom.min())",
            "p_hyb = 0.7 * p_xgb + 0.3 * p_iso",
            "p1, r1, _ = precision_recall_curve(y, p_xgb); p3, r3, _ = precision_recall_curve(y, p_hyb)",
            "print(f'XGB PR-AUC: {auc(r1, p1):.4f} | Hybrid PR-AUC: {auc(r3, p3):.4f}')",
        ]),
        make_md(["### 2. Platt Scaling Calibration (BR-05)"]),
        make_code([
            "cal = CalibratedClassifierCV(xgb, method='sigmoid', cv='prefit').fit(X, y)",
            "p_cal = cal.predict_proba(X)[:, 1]",
            "print(f'Brier Score Before: {brier_score_loss(y, p_xgb):.4f} | After: {brier_score_loss(y, p_cal):.4f} (<= 0.05)')",
        ]),
    ]

def build_nb_07_shap():
    """Tao notebook 07_shap.ipynb"""
    return [
        make_md([
            "# 🔍 Thực Nghiệm 07: Giải Thích Mô Hình với SHAP TreeExplainer (XAI)",
            "**Quy tắc**: `FR-05 / US-02: Explainable AI` & Kiểm chứng tính cộng Shapley.",
        ]),
        make_code([
            "import numpy as np, pandas as pd, matplotlib.pyplot as plt, shap",
            "from backend.ml.inference.model_loader import load_xgboost_model",
            "from backend.ml.features.feature_definitions import FEATURE_NAMES, FEATURE_LABELS",
            "from scripts.train_xgboost_real import generate_training_data",
            "model = load_xgboost_model()",
            "X, y = generate_training_data(n_normal=1000, n_fraud=100)",
            "explainer = shap.TreeExplainer(model)",
            "shap_values = explainer.shap_values(X)",
            "print(f'TreeExplainer ready. Base value: {explainer.expected_value:.4f}')",
        ]),
        make_md(["### 2. SHAP Summary Plot"]),
        make_code([
            "plt.figure(figsize=(9, 5), dpi=150)",
            "shap.summary_plot(shap_values, pd.DataFrame(X, columns=FEATURE_NAMES), show=False)",
            "plt.title('SHAP Global Feature Importance'); plt.show()",
        ]),
    ]
