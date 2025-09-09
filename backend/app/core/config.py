import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://lily:lily123@localhost:5432/lily_saas")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    PROJECT_NAME: str = "Lily AI"
    DEBUG: bool = True
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_STARTER: str = os.getenv("STRIPE_PRICE_STARTER", "")
    STRIPE_PRICE_PRO: str = os.getenv("STRIPE_PRICE_PRO", "")
    STRIPE_PRICE_GROWTH: str = os.getenv("STRIPE_PRICE_GROWTH", "")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")
    
    # Google Calendar
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "lily-ai-photos")
    
    # Cal.com
    CALCOM_API_KEY: str = os.getenv("CALCOM_API_KEY", "")
    CALCOM_WEBHOOK_SECRET: str = os.getenv("CALCOM_WEBHOOK_SECRET", "")
    
    # Application Settings
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "America/New_York")
    QUIET_HOURS_START: int = int(os.getenv("QUIET_HOURS_START", "21"))
    QUIET_HOURS_END: int = int(os.getenv("QUIET_HOURS_END", "9"))
    JITTER_MIN_SECONDS: int = int(os.getenv("JITTER_MIN_SECONDS", "10"))
    JITTER_MAX_SECONDS: int = int(os.getenv("JITTER_MAX_SECONDS", "45"))
    REVIEW_DELAY_HOURS: int = int(os.getenv("REVIEW_DELAY_HOURS", "24"))
    
    # Worker Configuration
    WORKER_CONCURRENCY: int = int(os.getenv("WORKER_CONCURRENCY", "4"))
    WORKER_POLL_INTERVAL: int = int(os.getenv("WORKER_POLL_INTERVAL", "1"))
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()