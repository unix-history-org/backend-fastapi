from typing import Optional, Any, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from src.app.core.db.base_layer import AbstractDatabaseLayer
from src.app.core.db.mongodb import db
from src.settings import settings


class MongoDBDatabaseLayer(AbstractDatabaseLayer):
    def __init__(self) -> None:
        self._client = db.client
        self.database = self._client.get_database(settings.MONGO_INITDB_DATABASE)
        self.id_key = "_id"

    async def get(self, name: str, filters: dict) -> Optional[dict]:
        collection = await self._get_collection(name)
        filters = await self._convert_filters_for_db_write(filters)
        return self._append_id_object(await collection.find_one(filters))

    async def get_all(self, name: str) -> Optional[list]:
        collection = await self._get_collection(name)
        return self._append_id_to_list(await collection.find().to_list(length=None))

    async def first(self, name: str) -> Optional[dict]:
        collection = await self._get_collection(name)
        return self._append_id_object(await collection.find_one())

    async def create(self, name: str, params: dict) -> dict:
        collection = await self._get_collection(name)
        item = await collection.insert_one(await self._convert_filters(params))
        return await self.get(name, {"_id": item.inserted_id})

    async def update(self, name: str, filters: dict, params: dict) -> Optional[dict]:
        collection = await self._get_collection(name)
        filters = await self._convert_filters_for_db_write(filters)
        params = await self._convert_params(params)
        await collection.update_one(filters, {"$set": params})
        ret = await self.get(name, filters)
        return self._append_id_object(ret)

    async def delete(self, name: str, filters: dict) -> bool:
        collection = await self._get_collection(name)
        filters = await self._convert_filters_for_db_write(filters)
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
        return {
            key: await self._convert_filters_value(key, value)
            for key, value in filters.items()
        }

    async def _convert_filters_for_db_write(self, filters: dict) -> dict:
        return {
            await self._convert_key(key): await self._convert_filters_value(key, value)
            for key, value in filters.items()
        }

    @staticmethod
    async def _convert_key(key):
        if key == "id":
            return "_id"
        return key

    @staticmethod
    async def _convert_filters_value(key: str, value: Any) -> Any:
        if "_id" in key or "id" in key:
            if isinstance(value, str):
                return ObjectId(value)
            if isinstance(value, list):
                return [ObjectId(value_one) for value_one in value]
        return value

    @staticmethod
    async def _convert_params(params: dict) -> dict:
        return {key: value for key, value in params.items() if value is not None}

    def _append_id_object(self, obj: dict) -> Optional[dict]:
        if obj is None:
            return None

        if obj.get(self.id_key) is None:
            return obj
        obj_id = {"id": str(obj.pop(self.id_key, "none"))}
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key] = self._convert_obj_id_to_str(value)
            if isinstance(value, list):
                obj[key] = self._convert_list_obj_id_to_list_str(value)

        return obj | obj_id

    @staticmethod
    def _convert_obj_id_to_str(value: ObjectId) -> str:
        return str(value)

    @staticmethod
    def _convert_list_obj_id_to_list_str(values: List[ObjectId | str]) -> List[str]:
        if len(values) == 0 or not isinstance(values[0], ObjectId):
            return values
        ret = []
        for value in values:
            ret.append(str(value))
        return ret

    def _append_id_to_list(self, objs: list) -> Optional[list]:
        if objs is None:
            return None

        ret_objs = []

        for obj in objs:
            ret_objs.append(self._append_id_object(obj))

        return ret_objs
