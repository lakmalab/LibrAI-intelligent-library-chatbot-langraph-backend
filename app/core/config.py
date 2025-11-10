from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "LibrAI – The Intelligent National Library Chat Assistant"
    APP_VERSION: str = "1.0.0"

    DEBUG:bool = False
    ALLOWED_ORIGINS: str = ""
    API_PREFIX:str = "/api"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str  = "mysql+pymysql://root:1234@localhost:3306/librelibraryassistant"

    SESSION_EXPIRE_HOURS: int
    OPENAI_API_KEY:str
    OPENAI_AI_MODEL:str
    API_BASE_URL: str = "http://localhost:8000"


    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()