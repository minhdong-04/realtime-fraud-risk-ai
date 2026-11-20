"""
{
    module : rate_limiter.py
    desc   : Bộ đếm giới hạn tần suất gọi API (Rate Limiter) trên Redis (1000 req/min/token).
}
"""

import time
from typing import Any

class RateLimiter:
    """
    {
        class  : RateLimiter
        desc   : Lớp quản lý giới hạn tần suất gọi API chống DDOS và kiểm soát tải
    }
    """

    def __init__(self, cache_adapter: Any = None, max_requests: int = 1000, window_seconds: int = 60) -> None:
        self._cache = cache_adapter
        self._max = max_requests
        self._window = window_seconds
        self._local_counts: dict[str, list[float]] = {}

    def is_rate_limited(self, identifier: str) -> bool:
        """
        {
            func   : is_rate_limited
            desc   : Kiểm tra xem identifier (token/IP) có vượt quá giới hạn request/phút hay không
            input  : identifier (str)
            output : (bool) — True nếu bị rate limit
            loop   : 1 loop — lọc các request quá thời gian cửa sổ window
        }
        """
        now = time.time()
        if identifier not in self._local_counts:
            self._local_counts[identifier] = []

        # { loop-1: loại bỏ các mốc thời gian ngoài cửa sổ window }
        self._local_counts[identifier] = [
            ts for ts in self._local_counts[identifier] if now - ts < self._window
        ]

        if len(self._local_counts[identifier]) >= self._max:
            return True

        self._local_counts[identifier].append(now)
        return False
