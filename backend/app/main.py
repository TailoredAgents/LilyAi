from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import settings

logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/")
async def root():
    return {"message": "Lily AI API", "version": "1.0.0", "status": "healthy"}

@app.get("/health")
async def health():
    return {"ok": True}

# Import and include routers
from app.api.webhooks.stripe import router as stripe_webhook_router
from app.api.webhooks.twilio_voice import router as twilio_voice_router  
from app.api.webhooks.calcom import router as calcom_webhook_router
from app.api.routes.billing import router as billing_router
from app.api.routes.leads import router as leads_router

# Include all routers
app.include_router(stripe_webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(twilio_voice_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(calcom_webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(billing_router, prefix=f"{settings.API_V1_PREFIX}/billing", tags=["billing"])
app.include_router(leads_router, prefix=f"{settings.API_V1_PREFIX}", tags=["leads"])