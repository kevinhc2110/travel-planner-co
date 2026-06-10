from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application."""

    app_name: str = "Travel Planner CO"

    gemini_api_key: str
    gemini_model: str
    gemini_embedding_model: str

    postgres_dsn: str

    postgres_user: str
    postgres_password: str
    postgres_db: str

    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
