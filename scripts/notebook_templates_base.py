"""
{
    module : notebook_templates_base.py
    desc   : Templates cho Notebooks 03 (Baseline Models) va 04 (Imbalanced Data).
}
"""

def make_md(lines):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in lines]}

def make_code(lines):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [l + "\n" for l in lines]}

def build_nb_03_baseline():
    """Tao notebook 03_baseline_models.ipynb"""
    return [
        make_md([
            "# 📊 Thực Nghiệm 03: So Sánh Các Mô Hình Baseline Phát Hiện Gian Lận",
            "**Tác giả**: Phan Võ Minh Đồng (DH52200514) | **Mục tiêu**: So sánh Logistic Regression (E01), Random Forest (E02), XGBoost (E03).",
        ]),
        make_code([
            "import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns",
            "from sklearn.linear_model import LogisticRegression",
            "from sklearn.ensemble import RandomForestClassifier",
            "from xgboost import XGBClassifier",
            "from sklearn.metrics import precision_recall_curve, roc_curve, auc, confusion_matrix",
            "from sklearn.model_selection import train_test_split",
            "from sklearn.preprocessing import StandardScaler",
            "import warnings; warnings.filterwarnings('ignore')",
            "print('-> Đã nạp thư viện.')",
        ]),
        make_md(["### 2. Nạp dữ liệu và EDA"]),
        make_code([
            "np.random.seed(42); n_samples = 40000; n_fraud = int(n_samples * 0.008); n_norm = n_samples - n_fraud",
            "X_norm = np.column_stack([np.random.poisson(1.2, n_norm), np.random.poisson(3.0, n_norm), np.random.exponential(5e5, n_norm), np.random.poisson(1.0, n_norm), np.random.uniform(1e6, 5e6, n_norm), np.random.uniform(0.5, 1.8, n_norm), np.random.binomial(1, 0.04, n_norm), np.random.binomial(1, 0.08, n_norm)])",
            "X_fr = np.column_stack([np.random.poisson(5.5, n_fraud), np.random.poisson(14.0, n_fraud), np.random.exponential(6e6, n_fraud), np.random.poisson(4.2, n_fraud), np.random.uniform(5e5, 2e6, n_fraud), np.random.uniform(4.0, 15.0, n_fraud), np.random.binomial(1, 0.75, n_fraud), np.random.binomial(1, 0.60, n_fraud)])",
            "X = np.vstack([X_norm, X_fr]); y = np.concatenate([np.zeros(n_norm), np.ones(n_fraud)])",
            "X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)",
            "scaler = StandardScaler(); X_tr_s = scaler.fit_transform(X_tr); X_te_s = scaler.transform(X_te)",
            "print(f'Train: {len(y_tr)} | Test: {len(y_te)}')",
        ]),
        make_md(["### 3. Huấn luyện và Đánh giá"]),
        make_code([
            "models = {",
            "    'Logistic Regression (E01)': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),",
            "    'Random Forest (E02)': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1),",
            "    'XGBoost (E03)': XGBClassifier(n_estimators=150, max_depth=5, scale_pos_weight=(len(y_tr)-y_tr.sum())/y_tr.sum(), eval_metric='aucpr', random_state=42),",
            "}",
            "preds, metrics = {}, []",
            "for name, m in models.items():",
            "    m.fit(X_tr_s, y_tr); prob = m.predict_proba(X_te_s)[:, 1]; preds[name] = prob",
            "    p, r, _ = precision_recall_curve(y_te, prob); fpr, tpr, _ = roc_curve(y_te, prob)",
            "    metrics.append({'Model': name, 'PR-AUC': round(auc(r, p), 4), 'ROC-AUC': round(auc(fpr, tpr), 4)})",
            "pd.DataFrame(metrics)",
        ]),
        make_md(["### 4. Đồ thị so sánh PR Curve"]),
        make_code([
            "plt.figure(figsize=(8, 5), dpi=150)",
            "for name, prob in preds.items():",
            "    p, r, _ = precision_recall_curve(y_te, prob)",
            "    plt.plot(r, p, lw=2, label=f'{name} (PR-AUC={auc(r, p):.3f})')",
            "plt.title('Precision-Recall Curve Comparison', fontweight='bold'); plt.xlabel('Recall'); plt.ylabel('Precision'); plt.legend(); plt.show()",
        ]),
    ]

def build_nb_04_imbalanced():
    """Tao notebook 04_imbalanced.ipynb"""
    return [
        make_md([
            "# ⚖️ Thực Nghiệm 04: Kỹ Thuật Xử Lý Dữ Liệu Mất Cân Bằng (Imbalanced Data)",
            "**Quy tắc nghiệp vụ**: `BR-06: SMOTE Train-Only Validation` — Chống rò rỉ dữ liệu.",
        ]),
        make_code([
            "import numpy as np, pandas as pd, matplotlib.pyplot as plt",
            "from xgboost import XGBClassifier",
            "from sklearn.metrics import precision_recall_curve, auc",
            "from sklearn.model_selection import StratifiedKFold",
            "from imblearn.over_sampling import SMOTE",
            "from imblearn.under_sampling import RandomUnderSampler",
            "from scripts.train_xgboost_real import generate_training_data",
            "X, y = generate_training_data(n_normal=25000, n_fraud=500)",
            "print(f'Mẫu: {len(y)} | Gian lận: {(y == 1).sum()}')",
        ]),
        make_md(["### 2. K-Fold CV Chứng minh BR-06"]),
        make_code([
            "skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)",
            "res = {'Baseline': [], 'scale_pos_weight': [], 'SMOTE (Train-Only)': [], 'Under-Sampling': []}",
            "for tr_idx, val_idx in skf.split(X, y):",
            "    X_tr, y_tr, X_v, y_v = X[tr_idx], y[tr_idx], X[val_idx], y[val_idx]",
            "    # 1. Base",
            "    m1 = XGBClassifier(n_estimators=80, max_depth=5, eval_metric='aucpr', random_state=42).fit(X_tr, y_tr)",
            "    p1, r1, _ = precision_recall_curve(y_v, m1.predict_proba(X_v)[:, 1]); res['Baseline'].append(auc(r1, p1))",
            "    # 2. Scale pos weight",
            "    spw = (len(y_tr)-y_tr.sum())/y_tr.sum()",
            "    m2 = XGBClassifier(n_estimators=80, max_depth=5, scale_pos_weight=spw, eval_metric='aucpr', random_state=42).fit(X_tr, y_tr)",
            "    p2, r2, _ = precision_recall_curve(y_v, m2.predict_proba(X_v)[:, 1]); res['scale_pos_weight'].append(auc(r2, p2))",
            "    # 3. SMOTE Train-Only",
            "    X_sm, y_sm = SMOTE(random_state=42).fit_resample(X_tr, y_tr)",
            "    m3 = XGBClassifier(n_estimators=80, max_depth=5, eval_metric='aucpr', random_state=42).fit(X_sm, y_sm)",
            "    p3, r3, _ = precision_recall_curve(y_v, m3.predict_proba(X_v)[:, 1]); res['SMOTE (Train-Only)'].append(auc(r3, p3))",
            "    # 4. Under-sampling",
            "    X_u, y_u = RandomUnderSampler(random_state=42).fit_resample(X_tr, y_tr)",
            "    m4 = XGBClassifier(n_estimators=80, max_depth=5, eval_metric='aucpr', random_state=42).fit(X_u, y_u)",
            "    p4, r4, _ = precision_recall_curve(y_v, m4.predict_proba(X_v)[:, 1]); res['Under-Sampling'].append(auc(r4, p4))",
            "pd.DataFrame([{'Method': k, 'Mean PR-AUC': np.mean(v), 'Std': np.std(v)} for k, v in res.items()])",
        ]),
    ]
