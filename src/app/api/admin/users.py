from typing import Optional, List

from fastapi import APIRouter, Cookie

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.app.schemas.users import UserAdminResponse
from src.app.schemas.base import MongoID
from src.app.service.user import UserService
from src.utils.tokens import check_token

router = APIRouter(prefix="/api/admin/user")


@router.post(
    "/edit_admin/{user_id}/{is_admin}",
    response_model=UserAdminResponse,
    status_code=200,
)
async def set_admin(
    user_id: MongoID, is_admin: bool, token: Optional[str] = Cookie(None)
) -> dict:
    await check_token(token)
    service = UserService(user_id, database=MongoDBDatabaseLayer())
    return await service.set_admin(is_admin=is_admin)


@router.get("/", response_model=List[UserAdminResponse], status_code=200)
async def get_admin_user_list(token: Optional[str] = Cookie(None)) -> List[dict]:
    await check_token(token)
    service = UserService(database=MongoDBDatabaseLayer())
    return await service.get()
