from typing import Optional, List

from fastapi import APIRouter, Cookie

from src.app.api.admin.utils import check_token
from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.app.schemas.users import (
    UserAdminResponse
)
from src.app.schemas.base import MongoID

from src.service.user import UserService

router = APIRouter(
    prefix="/api/admin/user"
)


@router.post('/set_admin/{user_id}', response_model=UserAdminResponse, status_code=200)
async def set_admin(user_id: MongoID, token: Optional[str] = Cookie(None)) -> UserAdminResponse:
    await check_token(token)
    service = UserService(user_id, database=MongoDBDatabaseLayer())
    return await service.set_admin()


@router.delete('/unset_admin/{user_id}', response_model=UserAdminResponse, status_code=200)
async def unset_admin(user_id: MongoID, token: Optional[str] = Cookie(None)) -> UserAdminResponse:
    await check_token(token)
    service = UserService(user_id, database=MongoDBDatabaseLayer())
    return await service.unset_admin()


@router.get('/', response_model=List[UserAdminResponse], status_code=200)
async def get_admin_user_list(token: Optional[str] = Cookie(None)) -> List[dict]:
    await check_token(token)
    service = UserService(database=MongoDBDatabaseLayer())
    return await service.get()
