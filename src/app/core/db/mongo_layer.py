from typing import Optional, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from src.app.core.db.base_layer import AbstractDatabaseLayer
from src.app.core.db.mongodb import db
from src.settings import settings


class MongoDBDatabaseLayer(AbstractDatabaseLayer):

    def __init__(self) -> None:
        self.client = db.client
        self.database = self.client.get_database(settings.MONGO_INITDB_DATABASE)

    async def get(self, name: str, filters: dict) -> Optional[dict]:
        collection = await self._get_collection(name)
        filters = await self._convert_filters(filters)
        return await collection.find_one(filters)

    async def get_all(self, name: str) -> Optional[list]:
        collection = await self._get_collection(name)
        return await collection.find().to_list(length=None)

    async def first(self, name: str) -> Optional[dict]:
        collection = await self._get_collection(name)
        return await collection.find_one()

    async def create(self, name: str, params: dict) -> dict:
        collection = await self._get_collection(name)
        item = await collection.insert_one(params)
        return await self.get(name, {"_id": item.inserted_id})

    async def update(self, name: str, filters: dict, params: dict) -> Optional[dict]:
        collection = await self._get_collection(name)
        filters = await self._convert_filters(filters)
        params = await self._convert_params(params)
        await collection.update_one(filters, {"$set": params})
        return await self.get(name, filters)

    async def delete(self, name: str, filters: dict) -> bool:
        collection = await self._get_collection(name)
        filters = await self._convert_filters(filters)
        res = await collection.delete_one(filters)
        return res.deleted_count == 1

    async def count(self, name: str, filters: dict) -> int:
        collection = await self._get_collection(name)
        return await collection.find(filters=filters).count()

    async def exists(self, name: str, filters: dict) -> bool:
        count = await self.count(name, filters)
        return count > 0

    async def _get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        return self.database.get_collection(collection_name)

    async def _convert_filters(self, filters: dict) -> dict:
        return {key: await self._convert_filters_value(key, value) for key, value in filters.items()}

    @staticmethod
    async def _convert_filters_value(key: str, value: Any) -> Any:
        return ObjectId(value) if "_id" in key or "id" in key else value

    @staticmethod
    async def _convert_params(params: dict) -> dict:
        return {key: value for key, value in params.items() if value is not None}
