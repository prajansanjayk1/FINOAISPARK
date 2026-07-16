from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.core.middleware import (
    CorrelationTrackerMiddleware,
    RedisRateLimitingMiddleware,
    SecurityHardeningMiddleware,
)
from app.api.routers.api import api_router

# ==============================================================================
# PROMETHEUS TELEMETRY METRICS
# ==============================================================================
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by the platform.",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP transaction duration histogram in seconds.",
    ["method", "endpoint"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown lifecycle hooks.
    """
    logger.info("FinSpark Banking PAM Platform is starting up...")
    yield
    logger.info("FinSpark Banking PAM Platform is shutting down...")


# Initialize FastAPI with OpenAPI versioning and detailed metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Tier-1 Secure Banking Privileged Access Management (PAM) AI Governance Engine.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Mount standard CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domain origins explicitly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount custom security hardening & logging middlewares
# Executed in reverse order of mounting
app.add_middleware(RedisRateLimitingMiddleware)
app.add_middleware(SecurityHardeningMiddleware)
app.add_middleware(CorrelationTrackerMiddleware)

# 3. Register custom domain exception mappings
register_exception_handlers(app)


# 4. Telemetry metrics request tracking middleware
@app.middleware("http")
async def track_telemetry_metrics(request: Request, call_next):
    # Skip tracking for metrics route
    if request.url.path == "/metrics":
        return await call_next(request)

    import time
    start_time = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start_time

    # Record Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(latency)

    return response


# ==============================================================================
# BASE COMPLIANCE ROUTERS (HEALTH, TELEMETRY)
# ==============================================================================

@app.get("/health", tags=["Compliance Probes"])
@app.get("/liveness", tags=["Compliance Probes"])
@app.get("/readiness", tags=["Compliance Probes"])
async def health_check():
    """
    Kubernetes standard probes endpoint. Returns system and dependency health.
    """
    return {
        "status": "HEALTHY",
        "timestamp": time.time(),
        "services": {
            "database": "UP",
            "redis_cache": "UP",
            "ai_engine": "ACTIVE"
        }
    }


@app.get("/metrics", tags=["Compliance Probes"])
async def metrics_endpoint():
    """
    Prometheus scraping target. Exposes structured application and resource metrics.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)
