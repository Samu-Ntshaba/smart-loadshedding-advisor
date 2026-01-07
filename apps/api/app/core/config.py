from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/smart_loadshedding"
    eskom_token_key: str | None = None
    openai_key: str | None = None


settings = Settings()
