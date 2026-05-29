from typing import Optional

from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./barber_api.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    TIME_ZONE: str = os.getenv("TIME_ZONE", "UTC")


settings: Settings = Settings()