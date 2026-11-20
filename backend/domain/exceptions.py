"""
{
    module : exceptions.py
    desc   : Phân cấp ngoại lệ (Exception Hierarchy) cho toàn bộ hệ thống phát hiện gian lận.
}
"""

class FraudPlatformError(Exception):
    """Exception gốc cho toàn bộ platform"""
    pass

class DomainError(FraudPlatformError):
    """Exception gốc cho các lỗi logic domain"""
    pass

class DuplicateCaseError(DomainError):
    """Xảy ra khi cố gắng tạo fraud case trùng lặp cho cùng một transaction"""
    pass

class CaseAlreadyClosedError(DomainError):
    """Xảy ra khi cố gắng chỉnh sửa một fraud case đã đóng (CLOSED)"""
    pass

class UnknownModelError(DomainError):
    """Xảy ra khi yêu cầu một mô hình ML chưa được đăng ký trong registry"""
    pass

class VelocityError(DomainError):
    """Xảy ra khi tham số tính toán velocity features không hợp lệ"""
    pass

class InfrastructureError(FraudPlatformError):
    """Exception gốc cho các lỗi tầng hạ tầng (infrastructure)"""
    pass

class RedisConnectionError(InfrastructureError):
    """Xảy ra khi thao tác với Redis thất bại"""
    pass

class ScoringError(FraudPlatformError):
    """Exception gốc cho các lỗi trong quá trình chấm điểm rủi ro (scoring engine)"""
    pass

class ScoringTimeoutError(ScoringError):
    """Xảy ra khi thời gian chấm điểm vượt quá SLA latency cho phép"""
    pass
