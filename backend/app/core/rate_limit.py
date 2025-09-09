from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import redis
import time
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class RateLimiter:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        try:
            pipe = self.redis_client.pipeline()
            now = time.time()
            window_start = now - window_seconds
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            request_count = results[1]
            
            if request_count >= max_requests:
                return False, max_requests - request_count
            
            return True, max_requests - request_count - 1
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            # Fail open - allow request if Redis is down
            return True, 0
    
    def get_tenant_key(self, tenant_id: str, endpoint: str = "") -> str:
        if endpoint:
            return f"rate_limit:tenant:{tenant_id}:{endpoint}"
        return f"rate_limit:tenant:{tenant_id}"
    
    def get_ip_key(self, ip: str, endpoint: str = "") -> str:
        if endpoint:
            return f"rate_limit:ip:{ip}:{endpoint}"
        return f"rate_limit:ip:{ip}"

rate_limiter = RateLimiter()

class RateLimitMiddleware:
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        by_tenant: bool = True
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.by_tenant = by_tenant
    
    async def __call__(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get identifier
        if self.by_tenant and hasattr(request.state, "tenant_id"):
            key = rate_limiter.get_tenant_key(
                request.state.tenant_id,
                request.url.path
            )
        else:
            client_ip = request.client.host
            key = rate_limiter.get_ip_key(client_ip, request.url.path)
        
        # Check rate limit
        allowed, remaining = rate_limiter.check_rate_limit(
            key,
            self.max_requests,
            self.window_seconds
        )
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": self.window_seconds
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window_seconds),
                    "Retry-After": str(self.window_seconds)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)
        
        return response