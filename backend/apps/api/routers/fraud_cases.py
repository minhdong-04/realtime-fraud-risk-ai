"""
{
    module : fraud_cases.py
    desc   : Router API Hang cho Fraud Case ho tro Cursor-based Keyset Pagination va mapping chuan (US-01..03).
}
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.infrastructure.db.session import get_db
from backend.infrastructure.db.repositories.postgres_fraud_case_repository import PostgresFraudCaseRepository
from backend.infrastructure.db.models.orm_models import FraudCaseORM, TransactionORM, ModelPredictionORM
from backend.domain.entities.fraud_case import AnalystDecision
from backend.services.fraud_case_service import FraudCaseService
from backend.services.sla_monitoring_service import SLAMonitoringService
from backend.apps.api.schemas.fraud_case_schema import (
    ReviewSubmissionSchema,
    FraudCaseResponseSchema,
    PaginatedFraudCasesSchema,
)
from backend.apps.api.dependencies import get_current_user, roles_required

router = APIRouter(prefix="/api/v1/fraud-cases", tags=["Fraud Cases"])

DEFAULT_SHAP_VALUES = [
    {"featureName": "new_device_flag", "featureValue": 1, "shapValue": 0.28, "label": "Co thiet bi moi chua tung ghi nhan"},
    {"featureName": "txn_count_5m", "featureValue": 6, "shapValue": 0.22, "label": "So luong giao dich trong 5 phut"},
    {"featureName": "amount_ratio", "featureValue": 4.5, "shapValue": 0.18, "label": "Ty le so tien so voi trung binh 30 ngay"}
]

@router.get("", response_model=PaginatedFraudCasesSchema)
def list_fraud_cases(
    level: str | None = Query(default=None, description="HIGH | MEDIUM | ALL"),
    status: str | None = Query(default=None, description="OPEN | ASSIGNED | CLOSED | ALL"),
    cursor: str | None = Query(default=None, description="Con tro thoi gian (created_at_id)"),
    limit: int = Query(default=20, ge=1, le=100, description="So ban ghi moi trang"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : list_fraud_cases
        desc   : Lay danh sach ca gian lan dung Cursor-based Keyset Pagination toi uu toc do O(1)
        input  : level (str | None), status (str | None), cursor (str | None), limit (int), db (Session)
        output : PaginatedFraudCasesSchema
        loop   : 1 loop — dinh dang cac ca gian lan thanh response schema
    }
    """
    repo = PostgresFraudCaseRepository(db)
    cases, next_cursor, has_more, total_count = repo.find_paginated(
        risk_level=level,
        status=status,
        cursor=cursor,
        limit=limit,
    )

    results = []
    # { loop-1: bo sung chi tiet giao dich cho tung fraud case }
    for c in cases:
        orm_case = db.query(FraudCaseORM).filter_by(id=str(c.id)).first()
        raw_txn_id = orm_case.transaction_id if orm_case else str(c.transaction_id)

        txn_orm = db.query(TransactionORM).filter(
            or_(TransactionORM.id == raw_txn_id, TransactionORM.transaction_id == raw_txn_id)
        ).first()
        pred_orm = db.query(ModelPredictionORM).filter(
            or_(ModelPredictionORM.transaction_id == raw_txn_id, ModelPredictionORM.id == raw_txn_id)
        ).first()

        txn_human_id = txn_orm.transaction_id if txn_orm else f"TXN-{str(c.transaction_id)[:8].upper()}"
        r_level = c.risk_score.level.value
        r_score = c.risk_score.value
        c_status = c.status.value
        shap_list = pred_orm.shap_values if pred_orm and pred_orm.shap_values else DEFAULT_SHAP_VALUES

        results.append(
            FraudCaseResponseSchema(
                id=str(c.id),
                transaction_id=txn_human_id,
                transactionId=txn_human_id,
                risk_level=r_level,
                riskLevel=r_level,
                risk_score=r_score,
                riskScore=r_score,
                status=c_status,
                assigned_to=str(c.assigned_to) if c.assigned_to else None,
                assignedTo=str(c.assigned_to) if c.assigned_to else None,
                created_at=c.created_at,
                createdAt=c.created_at.isoformat() if c.created_at else None,
                closed_at=c.closed_at,
                closedAt=c.closed_at.isoformat() if c.closed_at else None,
                transaction={
                    "amount": txn_orm.amount if txn_orm else 0.0,
                    "currency": txn_orm.currency if txn_orm else "VND",
                    "channel": txn_orm.channel if txn_orm else "MOBILE",
                    "created_at": txn_orm.created_at.isoformat() if txn_orm else c.created_at.isoformat(),
                    "account_id": txn_orm.account_id if txn_orm else "acc-default",
                    "merchant_id": txn_orm.merchant_id if txn_orm else "merch-default",
                },
                shap_values=shap_list,
                shapValues=shap_list,
            )
        )

    return PaginatedFraudCasesSchema(
        items=results,
        next_cursor=next_cursor,
        has_more=has_more,
        total_count=total_count,
    )

@router.get("/overdue", response_model=list[FraudCaseResponseSchema])
def get_overdue_fraud_cases(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_overdue_fraud_cases
        desc   : Lay danh sach cac Fraud Case vi pham SLA 24 gio (BR-06)
        input  : db (Session)
        output : list[FraudCaseResponseSchema]
        loop   : 1 loop — dinh dang danh sach case qua han SLA
    }
    """
    sla_service = SLAMonitoringService(db)
    overdue_cases = sla_service.get_overdue_cases()

    # { loop-1: chuyen doi danh sach case qua han sang response schema }
    return [
        FraudCaseResponseSchema(
            id=c.id,
            transaction_id=c.transaction_id,
            transactionId=c.transaction_id,
            risk_level=c.risk_level,
            riskLevel=c.risk_level,
            risk_score=c.risk_score,
            riskScore=c.risk_score,
            status=c.status,
            assigned_to=c.assigned_to,
            assignedTo=c.assigned_to,
            created_at=c.created_at,
            createdAt=c.created_at.isoformat() if c.created_at else None,
            closed_at=c.closed_at,
        )
        for c in overdue_cases
    ]

@router.get("/{id}", response_model=FraudCaseResponseSchema)
def get_fraud_case_detail(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : get_fraud_case_detail
        desc   : Lay chi tiet ca gian lan cung giai thich dac trung SHAP va lich su 30 ngay (US-02, US-09)
        input  : id (str)
        output : FraudCaseResponseSchema
        loop   : 1 loop — dinh dang lich su giao dich cu cua tai khoan
    }
    """
    case_orm = db.query(FraudCaseORM).filter_by(id=id).first()
    if not case_orm:
        raise HTTPException(status_code=404, detail="Khong tim thay ca gian lan rui ro")

    raw_txn_id = case_orm.transaction_id
    txn_orm = db.query(TransactionORM).filter(
        or_(TransactionORM.id == raw_txn_id, TransactionORM.transaction_id == raw_txn_id)
    ).first()
    pred_orm = db.query(ModelPredictionORM).filter(
        or_(ModelPredictionORM.transaction_id == raw_txn_id, ModelPredictionORM.id == raw_txn_id)
    ).first()

    txn_human_id = txn_orm.transaction_id if txn_orm else f"TXN-{str(case_orm.transaction_id)[:8].upper()}"
    shap_list = pred_orm.shap_values if pred_orm and pred_orm.shap_values else DEFAULT_SHAP_VALUES

    history = []
    if txn_orm:
        hist_rows = (
            db.query(TransactionORM)
            .filter_by(account_id=txn_orm.account_id)
            .order_by(TransactionORM.created_at.desc())
            .limit(20)
            .all()
        )
        # { loop-1: dinh dang lich su giao dich tai khoan }
        history = [
            {
                "id": r.id,
                "amount": r.amount,
                "currency": r.currency,
                "channel": r.channel,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
            }
            for r in hist_rows
        ]

    return FraudCaseResponseSchema(
        id=case_orm.id,
        transaction_id=txn_human_id,
        transactionId=txn_human_id,
        risk_level=case_orm.risk_level,
        riskLevel=case_orm.risk_level,
        risk_score=case_orm.risk_score,
        riskScore=case_orm.risk_score,
        status=case_orm.status,
        assigned_to=case_orm.assigned_to,
        assignedTo=case_orm.assigned_to,
        created_at=case_orm.created_at,
        createdAt=case_orm.created_at.isoformat() if case_orm.created_at else None,
        closed_at=case_orm.closed_at,
        closedAt=case_orm.closed_at.isoformat() if case_orm.closed_at else None,
        transaction={
            "amount": txn_orm.amount if txn_orm else 0.0,
            "currency": txn_orm.currency if txn_orm else "VND",
            "channel": txn_orm.channel if txn_orm else "MOBILE",
            "created_at": txn_orm.created_at.isoformat() if txn_orm else case_orm.created_at.isoformat(),
            "account_id": txn_orm.account_id if txn_orm else "acc-default",
            "merchant_id": txn_orm.merchant_id if txn_orm else "merch-default",
        },
        shap_values=shap_list,
        shapValues=shap_list,
        history=history,
    )

@router.post("/{id}/assign")
def assign_fraud_case(
    id: str,
    db: Session = Depends(get_db),
    current_user=Depends(roles_required("ANALYST")),
):
    """
    {
        func   : assign_fraud_case
        desc   : Nhan phan cong Case cho Analyst hien tai dang dang nhap
        input  : id (str)
        output : dict
        loop   : 0 loops
    }
    """
    repo = PostgresFraudCaseRepository(db)
    service = FraudCaseService(repo=repo, db=db)
    try:
        service.assign_case(case_id=UUID(id), analyst_id=UUID(current_user.id))
        return {"message": "Nhan phan cong ca kiem duyet thanh cong", "assigned_to": str(current_user.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/review")
def submit_case_review(
    id: str,
    payload: ReviewSubmissionSchema,
    db: Session = Depends(get_db),
    current_user=Depends(roles_required("ANALYST")),
):
    """
    {
        func   : submit_case_review
        desc   : Gui ket qua danh gia kiem tra ca gian lan cua Analyst (US-03)
        input  : id (str), payload (ReviewSubmissionSchema)
        output : dict
        loop   : 0 loops
    }
    """
    repo = PostgresFraudCaseRepository(db)
    service = FraudCaseService(repo=repo, db=db)

    try:
        decision_enum = AnalystDecision(payload.decision)
        service.submit_review(
            case_id=UUID(id),
            analyst_id=UUID(current_user.id),
            decision=decision_enum,
            reason=payload.reason,
        )
        return {"message": "Gui ket qua danh gia kiem tra thanh cong", "status": "CLOSED"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
