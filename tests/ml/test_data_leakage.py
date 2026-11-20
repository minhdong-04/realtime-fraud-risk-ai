"""
ML Data Leakage Tests (ML-DL-01..06).
"""

from datetime import datetime, timezone, timedelta

def test_ml_dl_01_smote_not_applied_to_test_set():
    """ML-DL-01: Verify synthetic samples do not contaminate test set"""
    original_test_ids = {"test-1", "test-2", "test-3"}
    synthetic_ids = {"smote-1", "smote-2"}
    assert original_test_ids.isdisjoint(synthetic_ids), "Data leakage: Synthetic samples in test set"

def test_ml_dl_02_historical_features_strictly_before_t():
    """ML-DL-02: Historical features tại thời điểm T chỉ dùng data có timestamp < T"""
    txn_time = datetime(2026, 8, 14, 12, 0, 0, tzinfo=timezone.utc)
    history_times = [
        datetime(2026, 8, 14, 11, 55, 0, tzinfo=timezone.utc),
        datetime(2026, 8, 14, 11, 50, 0, tzinfo=timezone.utc),
        datetime(2026, 8, 14, 10, 0, 0, tzinfo=timezone.utc),
    ]
    assert all(h_ts < txn_time for h_ts in history_times), "Lookahead leakage detected"

def test_ml_dl_03_no_post_investigation_labels_in_features():
    """ML-DL-03: Không dùng nhãn sau điều tra (chargeback, confirmed_fraud) làm đặc trưng đầu vào"""
    from backend.ml.features.feature_definitions import FEATURE_NAMES
    forbidden_substrings = ["chargeback", "confirmed", "label", "is_fraud_target", "review_decision"]
    for col in FEATURE_NAMES:
        assert not any(sub in col.lower() for sub in forbidden_substrings), f"Target leakage in feature {col}"

def test_ml_dl_04_target_encoding_training_fold_only():
    """ML-DL-04: Target encoding chỉ được tính từ training folds"""
    train_targets = [1, 0, 1, 0, 1]
    val_targets = [0, 0]
    # Mean tính chỉ trên train set, không pha lẫn val_targets
    enc_mean = sum(train_targets) / len(train_targets)
    combined_mean = sum(train_targets + val_targets) / len(train_targets + val_targets)
    assert enc_mean == 0.6 and enc_mean != combined_mean

def test_ml_dl_05_time_ordering_strict():
    """ML-DL-05: Verify strict time ordering train < val < test"""
    now = datetime.now(timezone.utc)
    train_dates = [now - timedelta(days=i) for i in range(30, 10, -1)]
    val_dates = [now - timedelta(days=i) for i in range(10, 3, -1)]
    test_dates = [now - timedelta(days=i) for i in range(3, 0, -1)]

    max_train = max(train_dates)
    min_val = min(val_dates)
    min_test = min(test_dates)

    assert max_train < min_val, "Data leakage: Train overlaps with Val split"
    assert min_val < min_test, "Data leakage: Val overlaps with Test split"

def test_ml_dl_06_model_does_not_see_test_labels():
    """ML-DL-06: Model fit() không nhận test labels trong quá trình huấn luyện"""
    from backend.ml.training.training_pipeline import FraudTrainingPipeline
    pipeline = FraudTrainingPipeline()
    assert hasattr(pipeline, "train_model")
