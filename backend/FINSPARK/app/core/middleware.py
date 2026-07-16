import time
import uuid
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings
from app.core.logging import correlation_id_ctx, trace_id_ctx, logger
from app.infrastructure.redis.service import redis_service


class SecurityHardeningMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting OWASP-compliant security headers to protect against
    XSS, Clickjacking, MIME-sniffing, and HSTS leakage.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Injection protection
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS (Enforced globally for HTTP/TLS connections)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        
        # Restrictive Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' ws: wss:;"
        )
        return response


class CorrelationTrackerMiddleware(BaseHTTPMiddleware):
    """
    Tracks, propagates, and logs a unique request Correlation-ID and Trace-ID.
    Saves IDs in a context-local thread safety store.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract headers or generate new UUIDs
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())

        # Set context variables for logger output binding
        correlation_id_token = correlation_id_ctx.set(correlation_id)
        trace_id_token = trace_id_ctx.set(trace_id)

        # Attach to request state for down-stream access
        request.state.correlation_id = correlation_id
        request.state.trace_id = trace_id

        # Track total request time
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
        finally:
            process_time = time.perf_counter() - start_time
            # Output execution logs
            logger.info(
                f"HTTP {request.method} {request.url.path} handled in {process_time:.4f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code if 'response' in locals() else 500,
                    "execution_time_seconds": process_time
                }
            )
            # Reset context vars to prevent memory leak
            correlation_id_ctx.reset(correlation_id_token)
            trace_id_ctx.reset(trace_id_token)

        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Trace-ID"] = trace_id
        return response


class RedisRateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Protects banking endpoints against brute force attacks and denial of service.
    Restricts IP client rate limits using a sliding window.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limit on standard health check endpoints
        if request.url.path in ("/health", "/liveness", "/readiness"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown-ip"
        limit_key = f"{client_ip}:{request.url.path}"

        # Standard banking limit: max 60 calls per minute per IP for sensitive APIs
        limit = 60
        period = 60

        is_allowed = redis_service.check_rate_limit(limit_key, limit, period)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip} on path {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many access requests. Please slow down and try again.",
                    "retry_after": period
                }
            )

        return await call_next(request)
