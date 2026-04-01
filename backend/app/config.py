from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
import sys
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path) if env_path.exists() else None,
        case_sensitive=False,
        extra="ignore",
    )

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""
    
    # AI Services
    openai_api_key: str = ""
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
    public_app_url: str = "http://127.0.0.1:3000"
    public_api_url: str = "http://127.0.0.1:8000/api"
    # Include 127.0.0.1 — browsers treat it as a different origin than "localhost".
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:19006"
    )
    
    # Feature Flags
    enable_ai_features: bool = True
    enable_payments: bool = True
    enable_test_login: bool = False
    test_login_email: str = "e2e@denevira.local"
    test_login_password: str = "DeneviraE2E123!"
    
    # AI Provider Selection
    ai_provider: str = "openai"

    # Upload limits
    max_upload_size_mb: int = 10
    progress_photo_storage_bucket: str = "progress-photos-private"
    progress_photo_signed_url_ttl_seconds: int = 3600

    # Weekly proof reminder
    enable_weekly_proof_reminders: bool = False
    weekly_proof_reminder_provider_ready: bool = False
    weekly_proof_reminder_channel: str = "email"
    weekly_proof_reminder_cooldown_hours: int = 144
    weekly_proof_reminder_job_interval_minutes: int = 60
    analytics_admin_emails: str = ""
    resend_webhook_secret: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

    # Fashn human parser (SegFormer) — default pulls from Hugging Face Hub
    fashn_human_parser_model: str = "fashn-ai/fashn-human-parser"
    # Dev-only: if HTTPS to huggingface.co fails (corporate MITM / cert issues), set True.
    # Do not enable in production.
    hf_hub_disable_ssl_verification: bool = False

    # ── Local CPU diffusion backend ──────────────────────────────────────────
    body_diffusion_backend: str = "sd15_inpaint_cpu"
    hf_token: str = ""
    hf_cache_dir: str = ""
    sd15_local_model_path: str = ""
    diffusion_roi_max_px: int = 512
    diffusion_num_steps: int = 18
    diffusion_use_openvino: bool = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def analytics_admin_emails_list(self) -> List[str]:
        return [email.strip().lower() for email in self.analytics_admin_emails.split(",") if email.strip()]

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


settings = Settings()
settings.validate_required()
