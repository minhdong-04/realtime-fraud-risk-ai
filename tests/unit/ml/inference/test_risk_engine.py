"""
Unit tests for Risk Engine and BR-03 policy (UT-RE-01..11).
"""

import pytest
from backend.ml.inference.risk_engine import compute_hybrid_score, RiskEngine
from backend.domain.policies.risk_threshold_policy import RiskThresholdPolicy
from backend.domain.value_objects.risk_score import RiskLevel

class TestRiskEngine:
    def test_ut_re_01_compute_hybrid_score_range(self):
        """UT-RE-01: Dải điểm hybrid luôn nằm trong khoảng [0, 100]"""
        score = compute_hybrid_score(fraud_proba=0.95, anomaly_score=0.90)
        assert 0 <= score <= 100

    def test_ut_re_02_compute_hybrid_score_zero(self):
        """UT-RE-02: Điểm hybrid bằng 0 khi cả hai xác suất bằng 0"""
        score = compute_hybrid_score(fraud_proba=0.0, anomaly_score=0.0)
        assert score == 0

    def test_ut_re_03_determine_risk_level_low(self):
        """UT-RE-03: Phân loại LOW khi score < 30"""
        policy = RiskThresholdPolicy()
        level = policy.determine_level(score=25, amount=100_000, is_new_device=False)
        assert level == RiskLevel.LOW

    def test_ut_re_04_determine_risk_level_medium(self):
        """UT-RE-04: Phân loại MEDIUM khi 30 <= score < 70"""
        policy = RiskThresholdPolicy()
        level = policy.determine_level(score=50, amount=100_000, is_new_device=False)
        assert level == RiskLevel.MEDIUM

    def test_ut_re_05_determine_risk_level_high(self):
        """UT-RE-05: Phân loại HIGH khi score >= 70"""
        policy = RiskThresholdPolicy()
        level = policy.determine_level(score=75, amount=100_000, is_new_device=False)
        assert level == RiskLevel.HIGH

    def test_ut_re_06_boundary_low_medium(self):
        """UT-RE-06: Boundary LOW/MEDIUM tại score = 30"""
        policy = RiskThresholdPolicy()
        level = policy.determine_level(score=30, amount=100_000, is_new_device=False)
        assert level == RiskLevel.MEDIUM

    def test_ut_re_07_boundary_medium_high(self):
        """UT-RE-07: Boundary MEDIUM/HIGH tại score = 70"""
        policy = RiskThresholdPolicy()
        level = policy.determine_level(score=70, amount=100_000, is_new_device=False)
        assert level == RiskLevel.HIGH

    def test_ut_re_08_br03_override_forces_high(self):
        """UT-RE-08: BR-03 override: amount > limit + new_device -> force HIGH"""
        policy = RiskThresholdPolicy(amount_override_limit=10_000_000.0)
        level = policy.determine_level(score=20, amount=50_000_000.0, is_new_device=True)
        assert level == RiskLevel.HIGH

    def test_ut_re_09_br03_not_triggered_for_known_device(self):
        """UT-RE-09: BR-03 NOT triggered: amount > limit nhưng NOT new_device"""
        policy = RiskThresholdPolicy(amount_override_limit=10_000_000.0)
        level = policy.determine_level(score=20, amount=50_000_000.0, is_new_device=False)
        assert level == RiskLevel.LOW

    def test_ut_re_10_fallback_scoring_engine(self):
        """UT-RE-10: RiskEngine chấm điểm an toàn với model rỗng"""
        engine = RiskEngine()
        fraud_proba, anomaly_score, risk_score = engine.evaluate({"amount": 100_000.0})
        assert risk_score.level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_ut_re_11_weights_sum_assertion(self):
        """UT-RE-11: Trọng số alpha + beta = 1.0"""
        score = compute_hybrid_score(fraud_proba=0.5, anomaly_score=0.5, alpha=0.7, beta=0.3)
        assert score == 50
