"""Kiểm thử hồi quy cho FeatureConsumer và ScoringConsumer sau khi vá lỗi import/biến."""

from backend.apps.worker.feature_consumer import FeatureConsumer
from backend.apps.worker.scoring_consumer import ScoringConsumer


def test_feature_and_scoring_consumers_pipeline() -> None:
    """FeatureConsumer tính đủ 8 đặc trưng và ScoringConsumer chấm điểm không ném NameError."""
    features = FeatureConsumer().process_event({"amount": 250_000.0})
    assert len(features) == 8

    result = ScoringConsumer().process_event(features)
    assert 0 <= result["score"] <= 100
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH"}

