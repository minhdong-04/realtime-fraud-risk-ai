"""
{
    module : fraud_case_schema.py
    desc   : Schema Pydantic cho yeu cau va phan hoi ca gian lan Fraud Case kem Cursor Pagination va ho tro alias snake/camelCase.
}
"""

from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

class ReviewSubmissionSchema(BaseModel):
    decision: str = Field(..., description="Quyet dinh kiem tra: LEGITIMATE | CONFIRMED_FRAUD | NEED_MORE_INFO")
    reason: str = Field(..., min_length=10, description="Giai trinh ly do bat buoc (toi thieu 10 ky tu)")

class FraudCaseResponseSchema(BaseModel):
    id: str
    transaction_id: str
    transactionId: str | None = None
    risk_level: str
    riskLevel: str | None = None
    risk_score: int
    riskScore: int | None = None
    status: str
    assigned_to: str | None = None
    assignedTo: str | None = None
    created_at: datetime
    createdAt: str | None = None
    closed_at: datetime | None = None
    closedAt: str | None = None
    transaction: dict[str, Any] | None = None
    shap_values: list[dict[str, Any]] | None = None
    shapValues: list[dict[str, Any]] | None = None
    history: list[dict[str, Any]] | None = None

class PaginatedFraudCasesSchema(BaseModel):
    items: list[FraudCaseResponseSchema]
    next_cursor: str | None = None
    has_more: bool = False
    total_count: int = 0
