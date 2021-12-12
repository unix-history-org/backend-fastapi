from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'unix-history.org backend'
    VERSION: str = '2.0.0'

    DATABASE_URL: Optional[str] = None
    MONGO_INITDB_DATABASE: Optional[str] = None

    class Config:
        case_sensitive = True


settings = Settings()
settings.DATABASE_URL = "mongodb://localhost:27017/unix-history"
settings.MONGO_INITDB_DATABASE = 'unix-history'
