from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Async URL used by the FastAPI application (asyncpg driver).
    DATABASE_URL: str
    # Sync URL used exclusively by Alembic migrations (psycopg2 driver).
    # Must point to the same database as DATABASE_URL.
    # Example: postgresql+psycopg2://user:pass@localhost/dbname
    MIGRATION_DATABASE_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
