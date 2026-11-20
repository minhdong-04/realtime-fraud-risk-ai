"""
{
    module : orm_models.py
    desc   : Các bảng ORM SQLAlchemy tương ứng với Từ điển dữ liệu (BA Phần 12).
}
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class UserORM(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="ANALYST")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class TransactionORM(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    account_id = Column(String(36), nullable=False, index=True)
    merchant_id = Column(String(36), nullable=False)
    device_id = Column(String(36), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="VND")
    transaction_type = Column(String(50), nullable=False, default="PURCHASE")
    channel = Column(String(50), nullable=False, default="WEB")
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    scored_at = Column(DateTime, nullable=True)

class ModelPredictionORM(Base):
    __tablename__ = "model_predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    fraud_probability = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    threshold_used = Column(Float, nullable=False, default=0.5)
    shap_values = Column(JSON, nullable=True)
    is_shadow = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class FraudCaseORM(Base):
    __tablename__ = "fraud_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), unique=True, nullable=False)
    risk_level = Column(String(20), nullable=False, default="HIGH")
    risk_score = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="OPEN")
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    closed_at = Column(DateTime, nullable=True)

class AnalystReviewORM(Base):
    __tablename__ = "analyst_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("fraud_cases.id"), nullable=False)
    analyst_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), nullable=False)
    actor_type = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36), nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class ModelVersionORM(Base):
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    version = Column(String(50), unique=True, nullable=False)
    pr_auc = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    brier_score = Column(Float, nullable=False)
    expected_cost = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="CANDIDATE")
    is_shadow = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    promoted_at = Column(DateTime, nullable=True)

class FraudLabelORM(Base):
    __tablename__ = "fraud_labels"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)
    label = Column(Integer, nullable=False)  # 1 = gian lận xác nhận, 0 = hợp lệ
    source = Column(String(50), nullable=False, default="ANALYST_REVIEW")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
