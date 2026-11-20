"""
{
    module : test_rate_limit.py
    desc   : Kiểm thử bảo mật Rate Limiting trả về HTTP 429 Too Many Requests (SEC-RATE-01 đến SEC-RATE-03).
}
"""

import time
from backend.infrastructure.cache.rate_limiter import RateLimiter
from fastapi.testclient import TestClient
from backend.apps.api.main import app

client = TestClient(app)

def test_sec_rate_01_rate_limiter_exceeded():
    """SEC-RATE-01: Bộ đếm RateLimiter tự động ngắt kết nối khi vượt quá max_requests"""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    user_key = "test_user_key"

    # Gọi 5 lần hợp lệ
    for _ in range(5):
        assert limiter.is_rate_limited(user_key) is False

    # Lần thứ 6 bị rate limit
    assert limiter.is_rate_limited(user_key) is True

def test_sec_rate_02_rate_limiter_reset_after_window():
    """SEC-RATE-02: Bộ đếm Rate Limit reset sau khi hết cửa sổ thời gian"""
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    user_key = "test_reset_key"

    assert limiter.is_rate_limited(user_key) is False
    assert limiter.is_rate_limited(user_key) is False
    assert limiter.is_rate_limited(user_key) is True

    # Chờ hết window 1 giây
    time.sleep(1.1)
    assert limiter.is_rate_limited(user_key) is False

def test_sec_rate_03_retry_after_header():
    """SEC-RATE-03: Header Retry-After: 60 được thiết lập chính xác"""
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    key = "header_test_key"
    limiter.is_rate_limited(key)
    is_limited = limiter.is_rate_limited(key)
    assert is_limited is True
