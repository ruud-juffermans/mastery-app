from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://mastery:mastery@localhost:5432/mastery"
    redis_url: str = "redis://localhost:6379/0"

settings = Settings()
