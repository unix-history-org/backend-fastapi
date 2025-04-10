from typing import Optional

from fastapi import HTTPException

from app.core.db.mongo_layer import MongoDBDatabaseLayer
from app.service.user import TokenService


async def check_token(token: Optional[str]):
    if not await TokenService(
        database=MongoDBDatabaseLayer()
    ).check_token_and_check_permission(token):
        raise HTTPException(status_code=403)
