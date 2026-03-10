from pydantic_settings import BaseSettings
from typing import List
import os
import sys
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: str
    
    # AI Services
    openai_api_key: str
    grok_api_key: str = ""
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    replicate_api_key: str = ""
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    
    # RevenueCat
    revenuecat_api_key: str = ""
    
    # Application
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:19006"
    
    # Feature Flags
    enable_ai_features: bool = True
    enable_payments: bool = True
    
    # AI Provider Selection
    ai_provider: str = "openai"

    # Upload limits
    max_upload_size_mb: int = 10
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024
    
    def validate_required(self):
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_key:
            missing.append("SUPABASE_SERVICE_KEY")
        if not self.supabase_anon_key:
            missing.append("SUPABASE_ANON_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if self.is_production:
            if not self.stripe_secret_key or self.stripe_secret_key.startswith("sk_test_"):
                missing.append("STRIPE_SECRET_KEY (live key required in production)")
            if self.cors_origins == "http://localhost:3000,http://localhost:19006":
                missing.append("CORS_ORIGINS (must set production domains)")
        if missing:
            print(f"WARNING: Missing/invalid env vars: {', '.join(missing)}", file=sys.stderr)
    
    class Config:
        env_file = str(env_path) if env_path.exists() else None
        case_sensitive = False
        extra = "ignore"


settings = Settings()
settings.validate_required()
