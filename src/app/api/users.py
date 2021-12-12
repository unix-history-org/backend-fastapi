from typing import Optional

from fastapi import APIRouter, HTTPException, Cookie

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.app.schemas.users import (
    UserResponse,
    UserCreation
)
from fastapi.responses import JSONResponse

from src.service.user import UserService

router = APIRouter(
    prefix="/api/user"
)


@router.post('/login', response_model=UserResponse, status_code=200)
async def login(params: UserCreation) -> JSONResponse:
    service = UserService(database=MongoDBDatabaseLayer())
    content, token = await service.login(params.dict())
    if 'detail' in content:
        raise HTTPException(status_code=401, detail=content['detail'])
    response = JSONResponse(content=content)
    response.set_cookie(key='token', value=token)
    return response


@router.post('/register', response_model=UserResponse, status_code=200)
async def register(params: UserCreation) -> JSONResponse:
    service = UserService(database=MongoDBDatabaseLayer())
    content, token = await service.register(params.dict())
    if 'detail' in content:
        raise HTTPException(status_code=401, detail=content['detail'])
    response = JSONResponse(content=content)
    response.set_cookie(key='token', value=token)
    return response


@router.post('/logout', response_model=bool, status_code=200)
async def logout(token: Optional[str] = Cookie(None)) -> dict:
    service = UserService(database=MongoDBDatabaseLayer())
    return await service.logout(token)

