from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./esl.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Cloudflare R2 (optional — only needed for media uploads)
    r2_account_id: str = ""
    r2_access_key: str = ""
    r2_secret_key: str = ""
    r2_bucket_name: str = ""
    r2_public_url: str = ""  # e.g. https://pub-xxxx.r2.dev

    # Anthropic (optional — only needed for AI question generation)
    anthropic_api_key: str = ""


settings = Settings()

# Render provides "postgres://" (or bare "postgresql://"). Name the driver
# explicitly: SQLAlchemy 2.1 made bare "postgresql://" default to psycopg 3,
# but requirements.txt installs psycopg2-binary.
for _prefix in ("postgres://", "postgresql://"):
    if settings.database_url.startswith(_prefix):
        settings.database_url = "postgresql+psycopg2://" + settings.database_url[len(_prefix):]
        break
