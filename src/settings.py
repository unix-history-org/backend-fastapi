from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "unix-history.org backend"  # pylint: disable=C0103
    VERSION: str = "2.0.0b1"  # pylint: disable=C0103

    BASE_URL: str = "localhost:8080"  # pylint: disable=C0103

    WEBSOCKET_TYPE: str = "ws"  # pylint: disable=C0103
    HTTP_OR_HTTPS: str = "http"  # pylint: disable=C0103

    DATABASE_URL: Optional[str] = "mongodb://localhost:27017/unix-history"  # pylint: disable=C0103
    MONGO_INITDB_DATABASE: Optional[str] = "unix-history"  # pylint: disable=C0103

    class Config:  # pylint: disable=R0903
        case_sensitive = True


settings = Settings()
