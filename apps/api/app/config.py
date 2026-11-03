from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Secrets come from the environment only."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sāntvana API"
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"),
    )
    database_url: str = "sqlite:///./santvana-dev.db"
    admin_api_token: str | None = None
    cors_origins: str = "http://localhost:3000"

    # Guest cart. The IP is stored only as a salted hash so reservation caps can
    # be enforced without keeping raw addresses.
    cart_ip_hash_secret: str | None = None

    # Razorpay. Keys come from the environment/.env only. Test keys (rzp_test_)
    # are the default; live keys are refused outside production.
    razorpay_key_id: str | None = None
    razorpay_key_secret: str | None = None
    razorpay_webhook_secret: str | None = None
    razorpay_api_base: str = "https://api.razorpay.com/v1"
    # Sandbox mode is for local review only. It never talks to Razorpay and is
    # refused when APP_ENV=production.
    razorpay_mock: bool = False
    order_payment_window_minutes: int = 10
    storefront_url: str = "http://localhost:3000"

    # Transactional email. Mailpit listens on localhost:1025 by default.
    mail_enabled: bool = True
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_starttls: bool = False
    mail_from: str = "orders@santvana.example"

    # Seller details are placeholders until the founder supplies them.
    seller_state: str = "[TO CONFIRM: founder]"
    seller_gstin: str = "[TO CONFIRM: founder]"

    otel_enabled: bool = False
    otel_service_name: str = "santvana-api"
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_otlp_headers: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def uses_live_razorpay_keys(self) -> bool:
        return any(
            (value or "").startswith("rzp_live_")
            for value in (self.razorpay_key_id, self.razorpay_key_secret)
        )

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
