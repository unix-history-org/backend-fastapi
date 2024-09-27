from motor.motor_asyncio import AsyncIOMotorClient

from settings import settings
from app.core.db.mongodb import db


async def connect() -> None:
    db.client = AsyncIOMotorClient(settings.DATABASE_URL)


async def disconnect() -> None:
    db.client.close()
