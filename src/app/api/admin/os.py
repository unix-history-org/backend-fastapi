from typing import Optional, List

from fastapi import APIRouter, Cookie

from app.core.db.mongo_layer import MongoDBDatabaseLayer
from app.schemas.os import OSAdmin, OSDatabase, OSAdminPatch
from app.schemas.base import MongoID
from app.service.os import OSService
from utils.tokens import check_token


router = APIRouter(prefix="/api/admin/os", tags=["admin os"])


@router.get("/{os_id}", response_model=OSAdmin, status_code=200)
async def get_admin_os(os_id: MongoID, token: Optional[str] = Cookie(None)) -> dict:
    await check_token(token)
    service = OSService(os_id, database=MongoDBDatabaseLayer())
    return await service.get()


@router.get("/", response_model=List[OSAdmin], status_code=200)
async def get_admin_os_list(token: Optional[str] = Cookie(None)) -> List[dict]:
    await check_token(token)
    service = OSService(database=MongoDBDatabaseLayer())
    ret = await service.get()
    return ret


@router.post("/", response_model=OSAdmin, status_code=200)
async def create_admin_os(
    params: OSDatabase, token: Optional[str] = Cookie(None)
) -> dict:
    await check_token(token)
    service = OSService(database=MongoDBDatabaseLayer())
    return await service.create(params.dict())


@router.put("/{os_id}", response_model=OSAdmin, status_code=200)
async def update_admin_os(
    os_id: str, params: OSAdminPatch, token: Optional[str] = Cookie(None)
) -> dict:
    await check_token(token)
    service = OSService(os_id, database=MongoDBDatabaseLayer())
    return await service.update(params.dict(exclude_unset=True))


@router.delete("/{os_id}", response_model=bool, status_code=200)
async def remove_admin_os(os_id: str, token: Optional[str] = Cookie(None)) -> bool:
    await check_token(token)
    service = OSService(os_id, database=MongoDBDatabaseLayer())
    return await service.remove()
