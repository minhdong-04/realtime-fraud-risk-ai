"""
{
    module : transaction_schema.py
    desc   : Schema Pydantic cho yêu cầu và phản hồi giao dịch Transaction.
}
"""

from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

class TransactionCreateSchema(BaseModel):
    transaction_id: str = Field(..., description="Mã định danh duy nhất của giao dịch phục vụ chống trùng lặp (Idempotency)")
    account_id: str = Field(..., description="ID tài khoản (UUID)")
    merchant_id: str = Field(..., description="ID merchant (UUID)")
    amount: float = Field(..., gt=0, description="Số tiền giao dịch phải lớn hơn 0")
    currency: str = Field(default="VND", description="Mã tiền tệ tiêu chuẩn ISO 4217")
    transaction_type: str = Field(default="PURCHASE", description="PURCHASE | TRANSFER | WITHDRAWAL | DEPOSIT")
    channel: str = Field(default="WEB", description="WEB | MOBILE | POS | API")
    device_id: str | None = Field(default=None, description="ID thiết bị (UUID)")

class TransactionResponseSchema(BaseModel):
    id: str
    transaction_id: str
    account_id: str
    merchant_id: str
    amount: float
    currency: str
    transaction_type: str
    channel: str
    status: str
    created_at: datetime
    scored_at: datetime | None = None
    risk_score: int | None = None
    risk_level: str | None = None
    fraud_probability: float | None = None
    shap_values: list[dict[str, Any]] | None = None
