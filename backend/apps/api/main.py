"""
{
    module : main.py
    desc   : Điểm khởi tạo chính cho ứng dụng FastAPI (Main Entry Point).
}
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.settings import settings
from backend.infrastructure.db.session import init_db
from backend.domain.exceptions import DomainError, ScoringError
from backend.apps.api.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.apps.api.middleware.latency_tracker import LatencyTrackerMiddleware
from backend.apps.api.routers import auth, transactions, fraud_cases, models, analytics, websocket, metrics, internal_scoring

app = FastAPI(
    title="Real-Time Fraud & Transaction Risk Detection Platform API",
    version="2.0.0",
    description="Hệ thống chấm điểm rủi ro giao dịch real-time, Explainable AI (SHAP) và giao diện hỗ trợ kiểm tra cho Fraud Analyst.",
)

# Cấu hình Latency Tracking Middleware (E1)
app.add_middleware(LatencyTrackerMiddleware)

# Cấu hình Rate Limiting Middleware (1000 req/min)
app.add_middleware(RateLimitMiddleware)

# Cấu hình middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bộ xử lý ngoại lệ trung tâm (Global Exception Handlers)
@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=422,
        content={"error": str(exc), "type": exc.__class__.__name__},
    )

@app.exception_handler(ScoringError)
async def scoring_exception_handler(request: Request, exc: ScoringError):
    return JSONResponse(
        status_code=503,
        content={"error": "Dịch vụ chấm điểm rủi ro tạm thời không khả dụng", "detail": str(exc)},
    )

# Đăng ký các API Routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(fraud_cases.router)
app.include_router(models.router)
app.include_router(analytics.router)
app.include_router(websocket.router)
app.include_router(metrics.router)
app.include_router(internal_scoring.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health", tags=["Health"])
def health_check():
    """
    {
        func   : health_check
        desc   : Endpoint kiểm tra trạng thái hoạt động của hệ thống (Health Check)
        input  : None
        output : dict — trạng thái OK
        loop   : 0 loops
    }
    """
    return {"status": "HEALTHY", "version": "2.0.0"}
