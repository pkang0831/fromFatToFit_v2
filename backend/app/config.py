from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

# Load .env from backend directory or parent
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
    grok_api_key: str
    gemini_api_key: str
    anthropic_api_key: str
    
    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str
    
    # RevenueCat
    revenuecat_api_key: str
    
    # Application
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:19006"
    
    # Feature Flags
    enable_ai_features: bool = True
    enable_payments: bool = True
    
    # AI Provider Selection (openai, grok, gemini, claude, hybrid)
    ai_provider: str = "openai"  # Default to OpenAI
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = str(env_path) if env_path.exists() else None
        case_sensitive = False


settings = Settings()
