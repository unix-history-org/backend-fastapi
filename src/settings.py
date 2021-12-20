from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "unix-history.org backend"  # pylint: disable=C0103
    VERSION: str = "2.0.0"  # pylint: disable=C0103

    BASE_URL: str = "localhost:8080"  # pylint: disable=C0103

    WEBSOCKET_TYPE: str = "ws"

    DATABASE_URL: Optional[str] = None  # pylint: disable=C0103
    MONGO_INITDB_DATABASE: Optional[str] = None  # pylint: disable=C0103

    class Config:
        case_sensitive = True


settings = Settings()
settings.DATABASE_URL = "mongodb://localhost:27017/unix-history"
settings.MONGO_INITDB_DATABASE = "unix-history"
