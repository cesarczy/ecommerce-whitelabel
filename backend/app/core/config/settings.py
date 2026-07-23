from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_debug: bool = True
    secret_key: str = "change-me-in-production"
    database_url: str = "postgresql+asyncpg://ecommerce:ecommerce@localhost:5432/ecommerce"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "amqp://ecommerce:ecommerce@localhost:5672//"
    use_celery_events: bool = False
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:4200"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "products"
    minio_secure: bool = False
    mercado_pago_access_token: str = ""
    stripe_secret_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/callback"
    seed_admin_enabled: bool = True
    seed_admin_email: str = "admin@ecommerce.local"
    seed_admin_password: str = "Admin123!"
    seed_admin_name: str = "Administrador"
    storage_provider: str = "minio"
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "ecommerce"
    r2_endpoint: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
