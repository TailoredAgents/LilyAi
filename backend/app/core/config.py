from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os
from pathlib import Path

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "Lily AI"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://lily:lily123@localhost:5432/lily_saas")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_STARTER: str = os.getenv("STRIPE_PRICE_STARTER", "")
    STRIPE_PRICE_PRO: str = os.getenv("STRIPE_PRICE_PRO", "")
    STRIPE_PRICE_GROWTH: str = os.getenv("STRIPE_PRICE_GROWTH", "")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Chatwoot
    CHATWOOT_API_URL: str = os.getenv("CHATWOOT_API_URL", "http://localhost:8080")
    CHATWOOT_API_KEY: str = os.getenv("CHATWOOT_API_KEY", "")
    CHATWOOT_ACCOUNT_ID: int = int(os.getenv("CHATWOOT_ACCOUNT_ID", "1"))
    CHATWOOT_WEBHOOK_SECRET: str = os.getenv("CHATWOOT_WEBHOOK_SECRET", "")
    
    # Cal.com
    CALCOM_API_KEY: str = os.getenv("CALCOM_API_KEY", "")
    CALCOM_WEBHOOK_SECRET: str = os.getenv("CALCOM_WEBHOOK_SECRET", "")
    CALCOM_DEFAULT_EVENT_TYPE_ID: str = os.getenv("CALCOM_DEFAULT_EVENT_TYPE_ID", "")
    
    # Google
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "lily-ai-photos")
    
    # n8n
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678")
    N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")
    
    # Meta
    META_APP_ID: str = os.getenv("META_APP_ID", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    META_VERIFY_TOKEN: str = os.getenv("META_VERIFY_TOKEN", "")
    
    # Feature Flags
    ENABLE_META_ADS: bool = os.getenv("ENABLE_META_ADS", "false").lower() == "true"
    ENABLE_GOOGLE_ADS: bool = os.getenv("ENABLE_GOOGLE_ADS", "false").lower() == "true"
    ENABLE_JOBBER_SYNC: bool = os.getenv("ENABLE_JOBBER_SYNC", "false").lower() == "true"
    ENABLE_HCP_SYNC: bool = os.getenv("ENABLE_HCP_SYNC", "false").lower() == "true"
    
    # Application Settings
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "America/New_York")
    QUIET_HOURS_START: int = int(os.getenv("QUIET_HOURS_START", "21"))
    QUIET_HOURS_END: int = int(os.getenv("QUIET_HOURS_END", "9"))
    JITTER_MIN_SECONDS: int = int(os.getenv("JITTER_MIN_SECONDS", "10"))
    JITTER_MAX_SECONDS: int = int(os.getenv("JITTER_MAX_SECONDS", "45"))
    MAX_QUOTE_PHOTOS: int = int(os.getenv("MAX_QUOTE_PHOTOS", "5"))
    QUOTE_CONFIDENCE_THRESHOLD: float = float(os.getenv("QUOTE_CONFIDENCE_THRESHOLD", "0.7"))
    
    # Worker
    WORKER_CONCURRENCY: int = int(os.getenv("WORKER_CONCURRENCY", "4"))
    WORKER_POLL_INTERVAL: int = int(os.getenv("WORKER_POLL_INTERVAL", "1"))
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()