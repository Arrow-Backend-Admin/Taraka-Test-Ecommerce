from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_ENVIRONMENTS = {"development", "test", "staging", "production"}


class Settings(BaseSettings):
    """Runtime configuration. Secrets come from the environment only.

    Values are validated when the object is built, so a malformed port, URL or
    environment name stops the process before the first request. Cross-field
    launch rules (static admin token in production, wildcard CORS, test keys in
    production) live in ``services.launch`` because they depend on the whole
    deployment, not one field.
    """

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
    max_request_bytes: int = Field(default=1_048_576, ge=1_024, le=10_485_760)

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
    razorpay_timeout_seconds: float = Field(default=20.0, gt=0, le=120)
    order_payment_window_minutes: int = Field(default=10, ge=1, le=120)
    storefront_url: str = "http://localhost:3000"

    # Transactional email. Mailpit listens on localhost:1025 by default.
    mail_enabled: bool = True
    smtp_host: str = "localhost"
    smtp_port: int = Field(default=1025, ge=1, le=65_535)
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_starttls: bool = False
    smtp_timeout_seconds: float = Field(default=15.0, gt=0, le=120)
    mail_from: str = "orders@santvana.example"
    outbox_max_attempts: int = Field(default=5, ge=1, le=20)

    # Seller details are placeholders until the founder supplies them.
    seller_state: str = "[TO CONFIRM: founder]"
    seller_gstin: str = "[TO CONFIRM: founder]"

    otel_enabled: bool = False
    otel_service_name: str = "santvana-api"
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_otlp_headers: str | None = None

    @field_validator("environment")
    @classmethod
    def _known_environment(cls, value: str) -> str:
        normalised = value.strip().lower()
        if normalised not in ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "APP_ENV must be one of " + ", ".join(sorted(ALLOWED_ENVIRONMENTS))
            )
        return normalised

    @field_validator("cors_origins")
    @classmethod
    def _cors_shape(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins:
            raise ValueError("CORS_ORIGINS must contain at least one origin")
        return ",".join(origins)

    @field_validator("razorpay_api_base")
    @classmethod
    def _https_api_base(cls, value: str) -> str:
        cleaned = value.strip().rstrip("/")
        local = cleaned.startswith(("http://localhost", "http://127.0.0.1"))
        if not cleaned.startswith("https://") and not local:
            raise ValueError("RAZORPAY_API_BASE must use https://")
        return cleaned

    @field_validator("smtp_host", "mail_from")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value must not be blank")
        return cleaned

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
    def uses_test_razorpay_keys(self) -> bool:
        return any(
            (value or "").startswith("rzp_test_")
            for value in (self.razorpay_key_id, self.razorpay_key_secret)
        )

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
