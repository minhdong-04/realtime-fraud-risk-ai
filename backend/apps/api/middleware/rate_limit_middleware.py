"""
{
    module : rate_limit_middleware.py
    desc   : Middleware kiểm tra giới hạn tần suất gọi API (1000 req/min/token).
}
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.infrastructure.cache.rate_limiter import RateLimiter

rate_limiter = RateLimiter(max_requests=1000, window_seconds=60)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    {
        class  : RateLimitMiddleware
        desc   : Middleware tự động chặn các request vượt quá 1000 req/phút và trả về HTTP 429
    }
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        {
            func   : dispatch
            desc   : Kiểm tra token/IP request và trả về 429 với Retry-After header nếu vi phạm
            input  : request (Request), call_next
            output : Response
            loop   : 0 loops
        }
        """
        # Bỏ qua kiểm tra rate limit cho các endpoint công khai như /health và docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/metrics"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        auth_header = request.headers.get("authorization", client_ip)

        if rate_limiter.is_rate_limited(auth_header):
            return Response(
                content='{"detail": "Vượt quá giới hạn 1000 request/phút. Thử lại sau."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        return await call_next(request)
