from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.api.routes import auth, tenants, leads, conversations, messages, quotes, bookings, reviews, billing, analytics
from app.api.webhooks import chatwoot, calcom, stripe

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Lily AI Backend", version="1.0.0")
    yield
    logger.info("Shutting down Lily AI Backend")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Lily AI API", "version": "1.0.0", "status": "healthy"}

@app.get("/health")
async def health_check():
    try:
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

# API Routes
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(tenants.router, prefix=f"{settings.API_V1_PREFIX}/tenants", tags=["tenants"])
app.include_router(leads.router, prefix=f"{settings.API_V1_PREFIX}/leads", tags=["leads"])
app.include_router(conversations.router, prefix=f"{settings.API_V1_PREFIX}/conversations", tags=["conversations"])
app.include_router(messages.router, prefix=f"{settings.API_V1_PREFIX}/messages", tags=["messages"])
app.include_router(quotes.router, prefix=f"{settings.API_V1_PREFIX}/quotes", tags=["quotes"])
app.include_router(bookings.router, prefix=f"{settings.API_V1_PREFIX}/bookings", tags=["bookings"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_PREFIX}/reviews", tags=["reviews"])
app.include_router(billing.router, prefix=f"{settings.API_V1_PREFIX}/billing", tags=["billing"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["analytics"])

# Webhook Routes
app.include_router(chatwoot.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(calcom.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(stripe.router, prefix="/webhooks", tags=["webhooks"])