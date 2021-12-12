from motor.motor_asyncio import AsyncIOMotorClient

from src.settings import settings
from src.app.core.db.mongodb import db


async def connect() -> None:
    db.client = AsyncIOMotorClient(settings.DATABASE_URL)


async def disconnect() -> None:
    db.client.close()
