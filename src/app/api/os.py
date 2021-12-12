from typing import List

from fastapi import APIRouter

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.app.schemas.os import (
    OSResponse
)
from src.app.schemas.base import MongoID
from src.service.os import OSService

router = APIRouter(
    prefix="/api/os"
)


@router.get('/', response_model=List[OSResponse], status_code=200)
async def get_os_list() -> List[dict]:
    service = OSService(database=MongoDBDatabaseLayer())
    return await service.get()


@router.get('/{os_id}', response_model=OSResponse, status_code=200)
async def get_os(os_id: MongoID) -> dict:
    service = OSService(os_id, database=MongoDBDatabaseLayer())
    return await service.get()
