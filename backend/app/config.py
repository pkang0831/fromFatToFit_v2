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
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3100,http://127.0.0.1:3100,http://localhost:19006"
    )
    
    # Feature Flags
    enable_ai_features: bool = True
    enable_payments: bool = True
    enable_test_login: bool = False
    test_login_email: str = "e2e@devenira.test"
    test_login_password: str = "DeneviraE2E123!"
    test_login_stub_user_id: str = "test-user-e2e"
    test_login_stub_access_token: str = "test-access-token"
    test_login_stub_refresh_token: str = "test-refresh-token"
    
    # AI Provider Selection
    ai_provider: str = "openai"
    openai_body_checkin_model: str = "gpt-5-mini"
    weekly_checkin_analysis_version: str = "v1"

    # Upload limits
    max_upload_size_mb: int = 10
    progress_photo_storage_bucket: str = "progress-photos-private"
    progress_photo_signed_url_ttl_seconds: int = 3600
    food_db_path: str = ""

    # Weekly proof reminder
    enable_weekly_proof_reminders: bool = False
    weekly_proof_reminder_provider_ready: bool = False
    weekly_scan_upload_first_handoff_enabled: bool = False
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

    # Web Push VAPID keys (generate once via: python -c "from pywebpush import Vapid; v=Vapid(); v.generate_keys(); print(v.public_key, v.private_key)")
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_claims_email: str = "mailto:noreply@devenira.com"

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

    @property
    def test_login_stub_mode(self) -> bool:
        return self.enable_test_login and (not self.supabase_url or not self.supabase_service_key)

    @staticmethod
    def _supabase_key_kind(value: str) -> str:
        token = (value or "").strip()
        if not token:
            return "missing"
        if token.startswith("sb_secret_"):
            return "sb_secret"
        if token.startswith("sb_publishable_"):
            return "sb_publishable"
        if token.startswith("eyJ"):
            return "jwt"
        return "other"
    
    def validate_required(self):
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_key:
            missing.append("SUPABASE_SERVICE_KEY")
        elif self._supabase_key_kind(self.supabase_service_key) == "sb_publishable":
            missing.append("SUPABASE_SERVICE_KEY (must be a service-role key, not sb_publishable)")
        if not self.supabase_anon_key:
            missing.append("SUPABASE_ANON_KEY")
        if self.enable_ai_features and self.ai_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if self.enable_payments and not self.stripe_secret_key:
            missing.append("STRIPE_SECRET_KEY")
        if self.is_production:
            if not self.stripe_secret_key or self.stripe_secret_key.startswith("sk_test_"):
                missing.append("STRIPE_SECRET_KEY (live key required in production)")
            if self.cors_origins == "http://localhost:3000,http://localhost:19006":
                missing.append("CORS_ORIGINS (must set production domains)")
        if missing:
            print(f"WARNING: Missing/invalid env vars: {', '.join(missing)}", file=sys.stderr)


settings = Settings()
settings.validate_required()
