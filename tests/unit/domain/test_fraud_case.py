"""
{
    module : test_fraud_case.py
    desc   : Kiểm thử đơn vị cho Domain Entity FraudCase (UT-DOM-01..05).
}
"""

import pytest
from uuid import uuid4
from backend.domain.entities.fraud_case import FraudCase, CaseStatus
from backend.domain.value_objects.risk_score import RiskScore, RiskLevel
from backend.domain.exceptions import CaseAlreadyClosedError

def test_ut_dom_01_fraud_case_creation():
    """UT-DOM-01: Tạo fraud case ở trạng thái OPEN mặc định"""
    score = RiskScore(value=85, level=RiskLevel.HIGH)
    case = FraudCase(transaction_id=uuid4(), risk_score=score)
    assert case.status == CaseStatus.OPEN
    assert case.assigned_to is None

def test_ut_dom_02_fraud_case_assign():
    """UT-DOM-02: Phân công case cho analyst"""
    score = RiskScore(value=85, level=RiskLevel.HIGH)
    case = FraudCase(transaction_id=uuid4(), risk_score=score)
    analyst_id = uuid4()
    case.assign(analyst_id)
    assert case.status == CaseStatus.ASSIGNED
    assert case.assigned_to == analyst_id

def test_ut_dom_03_prevent_reassign_when_closed():
    """UT-DOM-03: Ngăn phân công lại nếu case đã closed (BR-01, BR-04)"""
    score = RiskScore(value=85, level=RiskLevel.HIGH)
    case = FraudCase(transaction_id=uuid4(), risk_score=score)
    case.close()
    assert case.status == CaseStatus.CLOSED

    with pytest.raises(CaseAlreadyClosedError):
        case.assign(uuid4())

def test_ut_dom_04_close_sets_closed_at():
    """UT-DOM-04: close() chuyển status sang CLOSED và thiết lập closed_at"""
    score = RiskScore(value=90, level=RiskLevel.HIGH)
    case = FraudCase(transaction_id=uuid4(), risk_score=score)
    assert case.closed_at is None
    case.close()
    assert case.status == CaseStatus.CLOSED
    assert case.closed_at is not None

def test_ut_dom_05_risk_score_range_validation():
    """UT-DOM-05: RiskScore value phải trong khoảng [0, 100]"""
    valid_score = RiskScore(value=50, level=RiskLevel.MEDIUM)
    assert valid_score.value == 50

    with pytest.raises(Exception):
        RiskScore(value=150, level=RiskLevel.HIGH)
