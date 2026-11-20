"""
{
    module : i_model_repository.py
    desc   : Interface cho Repository quản lý phiên bản mô hình ML (Domain Layer).
}
"""

from abc import ABC, abstractmethod
from backend.domain.entities.model_version import ModelVersion

class IModelRepository(ABC):
    """
    {
        class  : IModelRepository
        desc   : Interface định nghĩa hợp đồng quản lý các phiên bản model ML trong registry
        note   : Cài đặt thực tế xử lý lưu trữ siêu dữ liệu phiên bản trong database
    }
    """

    @abstractmethod
    def save(self, model_version: ModelVersion) -> ModelVersion:
        """
        {
            func   : save
            desc   : Lưu thông tin phiên bản mô hình
            input  : model_version (ModelVersion)
            output : ModelVersion
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_by_version(self, version: str) -> ModelVersion | None:
        """
        {
            func   : find_by_version
            desc   : Tìm phiên bản mô hình theo chuỗi version (ví dụ: 'v1.0.0')
            input  : version (str)
            output : ModelVersion | None
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def find_production_model(self) -> ModelVersion | None:
        """
        {
            func   : find_production_model
            desc   : Lấy phiên bản mô hình đang hoạt động sản xuất (PRODUCTION)
            output : ModelVersion | None
            loop   : 0 loops
        }
        """
        ...

    @abstractmethod
    def list_all(self) -> list[ModelVersion]:
        """
        {
            func   : list_all
            desc   : Lấy danh sách tất cả các phiên bản mô hình trong hệ thống
            output : list[ModelVersion]
            loop   : 0 loops
        }
        """
        ...
