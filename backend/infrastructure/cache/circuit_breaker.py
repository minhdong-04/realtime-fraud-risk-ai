"""
{
    module : circuit_breaker.py
    desc   : Cài đặt Circuit Breaker Pattern để bảo vệ hệ thống khi Redis/Kafka gặp sự cố.
}
"""

import time
from typing import Callable, Any

class CircuitBreakerOpenException(Exception):
    """Ngoại lệ ném ra khi mạch đang ở trạng thái OPEN (Ngắt kết nối)"""
    pass

class CircuitBreaker:
    """
    {
        class  : CircuitBreaker
        desc   : Lớp quản lý trạng thái Circuit Breaker (CLOSED -> OPEN -> HALF-OPEN)
        pattern: Circuit Breaker Pattern
    }
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        self._threshold = failure_threshold
        self._timeout = recovery_timeout
        self._state = "CLOSED"
        self._failure_count = 0
        self._last_state_change = time.time()

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        {
            func   : execute
            desc   : Thực thi hàm gọi dịch vụ bên ngoài có bảo vệ bởi Circuit Breaker
            input  : func (Callable), args, kwargs
            output : Any
            loop   : 0 loops
        }
        """
        now = time.time()
        if self._state == "OPEN":
            if now - self._last_state_change > self._timeout:
                self._state = "HALF-OPEN"
            else:
                raise CircuitBreakerOpenException("Mạch đang đóng ngắt kết nối tạm thời do quá nhiều lỗi")

        try:
            result = func(*args, **kwargs)
            if self._state == "HALF-OPEN":
                self._state = "CLOSED"
                self._failure_count = 0
            return result
        except Exception as e:
            self._failure_count += 1
            if self._failure_count >= self._threshold:
                self._state = "OPEN"
                self._last_state_change = now
            raise e
