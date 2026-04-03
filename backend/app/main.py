# SPOORTHY QUANTUM OS — FastAPI Backend
# Full REST API with routers, auth, security, rate limiting

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import time
from typing import Dict, Any
import jwt
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .db.session import get_db, create_tables
from .core.config import settings
from .core.security import verify_pqc_signature, create_api_key
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from fastapi.responses import Response
from .api.v1.api import api_router
from .api.auth import router as auth_router, ensure_default_admin
from .core.logging_config import setup_logging
from backend.db.session import SessionLocal

# Setup structured logging
logger = structlog.get_logger()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Spoorthy Quantum OS API")
    await create_tables()
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("Shutting down Spoorthy Quantum OS API")

app = FastAPI(
    title="Spoorthy Quantum OS API",
    description="Quantum-accelerated accounting and financial services platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent")
    )

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s"
    )

    return response

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        url=str(request.url)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        url=str(request.url)
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Authentication dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_active_user(current_user: str = Depends(get_current_user)):
    # In a real app, you'd check user status in database
    return current_user

def check_role(required_role: str):
    def role_checker(current_user: str = Depends(get_current_active_user)):
        # user_id is the 'sub' claim; role is the 'role' claim
        # get_current_user only returns user_id string — extend to return full payload if role checks are needed
        # For now raise 403 for any role other than 'admin' until full RBAC is wired in
        raise HTTPException(status_code=403, detail="Role-based access control not yet implemented")
    return role_checker

# API Key authentication
async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # In a real app, you'd verify against database
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key

# PQC Signature verification
async def verify_signature(request: Request, body: bytes = None):
    signature = request.headers.get("X-PQC-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="PQC signature required")

    if body and not verify_pqc_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid PQC signature")

    return signature

# Health check
@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Metrics endpoint (for Prometheus)
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Auth endpoints
@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, username: str, password: str):
    # Credentials must be verified against the database.
    # This stub always rejects to prevent accidental bypass in production.
    # Use the /api/v1 auth router (backend/app/api/auth.py) for real logins.
    raise HTTPException(status_code=501, detail="Use /api/v1/auth/login")

@app.post("/auth/api-key")
async def generate_api_key(current_user: str = Depends(get_current_active_user)):
    api_key = create_api_key()
    # In a real app, you'd store this in database
    return {"api_key": api_key}

# Include API routers
app.include_router(auth_router, prefix="/api/v1")

app.include_router(
    api_router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_active_user)]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Spoorthy Quantum OS API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
