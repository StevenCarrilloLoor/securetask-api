"""Configuración central de la aplicación (12-factor: variables de entorno)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "SecureTask API"
    API_V1_PREFIX: str = "/api/v1"

    # NOTA DE SEGURIDAD: valor por defecto solo para desarrollo.
    # En producción DEBE inyectarse por variable de entorno SECRET_KEY.
    SECRET_KEY: str = "dev-secret-change-me"  # nosec-example: hallazgo esperado por el SAST
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite:///./securetask.db"


settings = Settings()
