from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "SUPER_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DB_NAME: str = "app.db"

    # для указания .env-файла используем модель конфигурации
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
