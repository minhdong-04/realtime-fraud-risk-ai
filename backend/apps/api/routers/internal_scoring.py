"""
{
    module : internal_scoring.py
    desc   : Router chấm điểm nội bộ cho hệ thống Core Banking (Yêu cầu X-Internal-API-Key).
}
"""

import hmac

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.infrastructure.db.session import get_db
from backend.apps.api.schemas.transaction_schema import TransactionCreateSchema
from backend.core.settings import settings
from backend.services.scoring_service import ScoringService

router = APIRouter(prefix="/internal/v1", tags=["Internal Scoring"])

@router.post("/score")
def internal_score_transaction(
    payload: TransactionCreateSchema,
    x_internal_api_key: str = Header(..., alias="X-Internal-API-Key"),
    db: Session = Depends(get_db),
):
    """
    {
        func   : internal_score_transaction
        desc   : Endpoint chấm điểm rủi ro trực tiếp cho Core Banking qua API Key
        input  : payload (TransactionCreateSchema), x_internal_api_key (str)
        output : dict — kết quả chấm điểm
        loop   : 0 loops
    }
    """
    if not hmac.compare_digest(x_internal_api_key.encode(), settings.internal_api_key.encode()):
        raise HTTPException(status_code=403, detail="Xác thực Internal API Key thất bại")

    service = ScoringService(db)
    result = service.score_transaction(payload.model_dump())
    return result
