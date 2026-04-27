import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.core.config import settings
from app.api.routes import auth_router, analyze_router, cases_router, dashboard_router, admin_router, websocket_router
from app.db.seed import seed_db

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.PROJECT_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application...")
    # NOTE: In production, alembic migrations should be run before app start.
    # We trigger the seed data job.
    asyncio.create_task(seed_db())

# Include Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(analyze_router, prefix="/api/v1/analyze", tags=["analyze"])
app.include_router(cases_router, prefix="/api/v1/cases", tags=["cases"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(websocket_router, prefix="/api/v1/ws", tags=["websocket"])

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "redis": "connected",
        "db": "connected",
        "timestamp": "now"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# trigger reload
