"""
{
    module : train_xgboost_real.py
    desc   : Train XGBoost tren 8 runtime features va luu artifact .joblib.
}
"""

import numpy as np
from xgboost import XGBClassifier
import joblib
import os

FEATURES = [
    "txn_count_5m", "txn_count_1h", "amount_sum_1h",
    "unique_merchants_1h", "avg_amount_30d", "amount_ratio",
    "new_device_flag", "new_merchant_flag",
]


def generate_training_data(n_normal=20000, n_fraud=2000):
    """
    {
        func   : generate_training_data
        desc   : Tao du lieu huan luyen tu phan phoi thuc te cho 8 dac trung runtime
        input  : n_normal (int), n_fraud (int)
        output : tuple[np.ndarray, np.ndarray] — X va y
        loop   : 0 loops
    }
    """
    rng = np.random.RandomState(42)

    # Giao dich binh thuong: it giao dich, so tien on dinh, thiet bi quen
    normal = np.column_stack([
        rng.poisson(1, n_normal),             # txn_count_5m: 0-3
        rng.poisson(3, n_normal),             # txn_count_1h: 1-8
        rng.exponential(500000, n_normal),     # amount_sum_1h
        rng.poisson(1, n_normal),             # unique_merchants_1h
        rng.uniform(1e6, 5e6, n_normal),      # avg_amount_30d
        rng.uniform(0.2, 2.0, n_normal),      # amount_ratio: gan 1.0
        rng.binomial(1, 0.05, n_normal),      # new_device_flag: 5%
        rng.binomial(1, 0.1, n_normal),       # new_merchant_flag: 10%
    ])

    # Giao dich gian lan: nhieu giao dich, so tien dot bien, thiet bi la
    fraud = np.column_stack([
        rng.poisson(5, n_fraud),              # txn_count_5m: 3-10
        rng.poisson(12, n_fraud),             # txn_count_1h: 8-20
        rng.exponential(5000000, n_fraud),     # amount_sum_1h: cao
        rng.poisson(4, n_fraud),              # unique_merchants_1h: nhieu
        rng.uniform(500000, 3e6, n_fraud),    # avg_amount_30d: thap hon
        rng.uniform(3.0, 20.0, n_fraud),      # amount_ratio: cao bat thuong
        rng.binomial(1, 0.7, n_fraud),        # new_device_flag: 70%
        rng.binomial(1, 0.5, n_fraud),        # new_merchant_flag: 50%
    ])

    X = np.vstack([normal, fraud]).astype(np.float32)
    y = np.concatenate([np.zeros(n_normal), np.ones(n_fraud)]).astype(int)

    # Xao tron du lieu
    idx = rng.permutation(len(y))
    return X[idx], y[idx]


def train_and_save():
    """
    {
        func   : train_and_save
        desc   : Huan luyen XGBoost va luu model artifact
        input  : None
        output : None
        loop   : 0 loops
    }
    """
    X, y = generate_training_data()
    pos = y.sum()
    neg = len(y) - pos
    print(f"Training data: {len(y)} mau ({int(neg)} normal, {int(pos)} fraud)")
    print(f"scale_pos_weight = {neg / max(1, pos):.2f}")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=neg / max(1, pos),
        eval_metric="aucpr",
        random_state=42,
        use_label_encoder=False,
    )
    model.fit(X, y)

    # Danh gia nhanh
    from sklearn.metrics import (
        precision_recall_curve, auc, classification_report
    )
    proba = model.predict_proba(X)[:, 1]
    prec, rec, _ = precision_recall_curve(y, proba)
    pr_auc = auc(rec, prec)
    print(f"PR-AUC (train): {pr_auc:.4f}")
    print(classification_report(y, model.predict(X), digits=4))

    out_path = os.path.join("backend", "ml", "artifacts", "xgboost_hybrid_v1.0.0.joblib")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(model, out_path)
    print(f"Model da luu tai: {out_path}")
    print(f"Feature names: {FEATURES}")


if __name__ == "__main__":
    train_and_save()
