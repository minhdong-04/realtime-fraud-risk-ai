"""
{
    module : postgres_model_repository.py
    desc   : Cài đặt thực tế của IModelRepository bằng SQLAlchemy / Postgres.
}
"""

from uuid import UUID
from sqlalchemy.orm import Session
from backend.domain.entities.model_version import ModelVersion, ModelStatus
from backend.domain.repositories.i_model_repository import IModelRepository
from backend.infrastructure.db.models.orm_models import ModelVersionORM

class PostgresModelRepository(IModelRepository):
    """
    {
        class  : PostgresModelRepository
        desc   : Lớp Repository tương tác lưu trữ cho đối tượng ModelVersion trong registry
        pattern: Repository Pattern
    }
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, model_version: ModelVersion) -> ModelVersion:
        """
        {
            func   : save
            desc   : Lưu hoặc cập nhật phiên bản mô hình trong cơ sở dữ liệu
            input  : model_version (ModelVersion)
            output : ModelVersion
            loop   : 0 loops
        }
        """
        existing = self._db.query(ModelVersionORM).filter_by(version=model_version.version).first()
        if existing:
            existing.status = model_version.status.value
            existing.is_shadow = model_version.is_shadow
            existing.promoted_at = model_version.promoted_at
        else:
            orm = ModelVersionORM(
                id=str(model_version.id),
                name=model_version.name,
                version=model_version.version,
                pr_auc=model_version.pr_auc,
                recall=model_version.recall,
                precision=model_version.precision,
                f1_score=model_version.f1_score,
                brier_score=model_version.brier_score,
                expected_cost=model_version.expected_cost,
                status=model_version.status.value,
                is_shadow=model_version.is_shadow,
                created_at=model_version.created_at,
                promoted_at=model_version.promoted_at,
            )
            self._db.add(orm)

        self._db.commit()
        return model_version

    def find_by_version(self, version: str) -> ModelVersion | None:
        """
        {
            func   : find_by_version
            desc   : Tìm phiên bản mô hình theo mã định danh version
            input  : version (str)
            output : ModelVersion | None
            loop   : 0 loops
        }
        """
        orm = self._db.query(ModelVersionORM).filter_by(version=version).first()
        if not orm:
            return None
        return self._to_domain(orm)

    def find_production_model(self) -> ModelVersion | None:
        """
        {
            func   : find_production_model
            desc   : Truy vấn mô hình đang ở trạng thái PRODUCTION
            output : ModelVersion | None
            loop   : 0 loops
        }
        """
        orm = self._db.query(ModelVersionORM).filter_by(status=ModelStatus.PRODUCTION.value).first()
        if not orm:
            return None
        return self._to_domain(orm)

    def list_all(self) -> list[ModelVersion]:
        """
        {
            func   : list_all
            desc   : Truy vấn tất cả các phiên bản mô hình, sắp xếp theo thời gian tạo giảm dần
            output : list[ModelVersion]
            loop   : 1 loop — chuyển đổi các bản ghi ORM sang thực thể Domain
        }
        """
        rows = self._db.query(ModelVersionORM).order_by(ModelVersionORM.created_at.desc()).all()
        # { loop-1: chuyển đổi từng bản ghi ORM thành ModelVersion }
        return [self._to_domain(row) for row in rows]

    def _to_domain(self, orm: ModelVersionORM) -> ModelVersion:
        """
        {
            func   : _to_domain
            desc   : Ánh xạ ModelVersionORM sang thực thể ModelVersion
            input  : orm (ModelVersionORM)
            output : ModelVersion
            loop   : 0 loops
        }
        """
        return ModelVersion(
            id=UUID(orm.id),
            name=orm.name,
            version=orm.version,
            pr_auc=orm.pr_auc,
            recall=orm.recall,
            precision=orm.precision,
            f1_score=orm.f1_score,
            brier_score=orm.brier_score,
            expected_cost=orm.expected_cost,
            status=ModelStatus(orm.status),
            is_shadow=orm.is_shadow,
            created_at=orm.created_at,
            promoted_at=orm.promoted_at,
        )
