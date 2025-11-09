from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "LibrAI – The Intelligent National Library Chat Assistant"
    APP_VERSION: str = "1.0.0"

    DEBUG:bool = False
    ALLOWED_ORIGINS: str = ""
    API_PREFIX:str = "/api"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str

    SESSION_EXPIRE_HOURS: int
    OPENAI_API_KEY:str
    OPENAI_AI_MODEL:str
    API_BASE_URL: str = "http://localhost:8000"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()