"""
{
    module : models.py
    desc   : Router API MLOps Registry quản lý các phiên bản mô hình và thăng cấp phát hành (US-05, US-06).
}
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.infrastructure.db.session import get_db
from backend.infrastructure.db.repositories.postgres_model_repository import PostgresModelRepository
from backend.domain.entities.model_version import ModelVersion, ModelStatus
from backend.apps.api.dependencies import get_current_user, roles_required

router = APIRouter(prefix="/api/v1/models", tags=["Models"])

class ModelResponseSchema(BaseModel):
    id: str
    name: str
    version: str
    pr_auc: float
    recall: float
    precision: float
    f1_score: float
    brier_score: float
    expected_cost: float
    status: str
    is_shadow: bool
    created_at: str

@router.get("", response_model=list[ModelResponseSchema])
def list_models(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    {
        func   : list_models
        desc   : Lấy danh sách các phiên bản mô hình trong registry cùng các chỉ số so sánh hiệu năng (US-05)
        input  : db (Session)
        output : list[ModelResponseSchema]
        loop   : 1 loop — định dạng thông tin các phiên bản mô hình
    }
    """
    repo = PostgresModelRepository(db)
    models = repo.list_all()

    if not models:
        v1 = ModelVersion(
            name="xgboost_hybrid",
            version="v1.0.0",
            pr_auc=0.54,
            recall=0.79,
            precision=0.64,
            f1_score=0.71,
            brier_score=0.062,
            expected_cost=1250.0,
            status=ModelStatus.PRODUCTION,
        )
        v2 = ModelVersion(
            name="xgboost_hybrid",
            version="v1.1.0-candidate",
            pr_auc=0.61,
            recall=0.86,
            precision=0.70,
            f1_score=0.77,
            brier_score=0.044,
            expected_cost=890.0,
            status=ModelStatus.CANDIDATE,
            is_shadow=True,
        )
        repo.save(v1)
        repo.save(v2)
        models = [v1, v2]

    # { loop-1: định dạng thực thể phiên bản mô hình thành response DTO }
    return [
        ModelResponseSchema(
            id=str(m.id),
            name=m.name,
            version=m.version,
            pr_auc=m.pr_auc,
            recall=m.recall,
            precision=m.precision,
            f1_score=m.f1_score,
            brier_score=m.brier_score,
            expected_cost=m.expected_cost,
            status=m.status.value,
            is_shadow=m.is_shadow,
            created_at=m.created_at.isoformat(),
        )
        for m in models
    ]

@router.post("/{version}/promote")
def promote_model(
    version: str,
    db: Session = Depends(get_db),
    current_user=Depends(roles_required("ML_ENGINEER")),
):
    """
    {
        func   : promote_model
        desc   : Thăng cấp phiên bản mô hình ứng viên sang chạy thực tế PRODUCTION (US-05)
        input  : version (str) — chuỗi mã phiên bản
        output : dict — { message, version, status }
        loop   : 1 loop — chuyển các phiên bản PRODUCTION cũ sang RETIRED
    }
    """
    repo = PostgresModelRepository(db)
    target = repo.find_by_version(version)
    if not target:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy phiên bản mô hình {version}")

    all_models = repo.list_all()
    # { loop-1: chuyển đổi các mô hình PRODUCTION cũ sang trạng thái RETIRED }
    for m in all_models:
        if m.status == ModelStatus.PRODUCTION:
            m.retire()
            repo.save(m)

    target.promote()
    repo.save(target)
    return {"message": f"Mô hình phiên bản {version} đã được thăng cấp lên PRODUCTION", "version": version, "status": "PRODUCTION"}

@router.post("/{version}/rollback")
def rollback_model(
    version: str,
    db: Session = Depends(get_db),
    current_user=Depends(roles_required("ML_ENGINEER")),
):
    """
    {
        func   : rollback_model
        desc   : Khôi phục lại phiên bản mô hình trước đó làm Champion (BR-09)
        input  : version (str)
        output : dict — { message, version, status }
        loop   : 1 loop — cập nhật trạng thái các model khác
    }
    """
    repo = PostgresModelRepository(db)
    target = repo.find_by_version(version)
    if not target:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy phiên bản mô hình {version}")

    all_models = repo.list_all()
    # { loop-1: đưa các model hiện tại về trạng thái RETIRED }
    for m in all_models:
        if m.version != version and m.status == ModelStatus.PRODUCTION:
            m.retire()
            repo.save(m)

    target.status = ModelStatus.PRODUCTION
    repo.save(target)
    return {"message": f"Đã rollback thành công về phiên bản {version}", "version": version, "status": "PRODUCTION"}

@router.post("/{version}/shadow")
def toggle_shadow_mode(
    version: str,
    db: Session = Depends(get_db),
    current_user=Depends(roles_required("ML_ENGINEER")),
):
    """
    {
        func   : toggle_shadow_mode
        desc   : Bật/Tắt chế độ chạy ngầm thử nghiệm Shadow Deployment cho phiên bản mô hình (US-06)
        input  : version (str)
        output : dict — { version, is_shadow }
        loop   : 0 loops
    }
    """
    repo = PostgresModelRepository(db)
    target = repo.find_by_version(version)
    if not target:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy phiên bản mô hình {version}")

    target.is_shadow = not target.is_shadow
    repo.save(target)
    return {"version": version, "is_shadow": target.is_shadow}
