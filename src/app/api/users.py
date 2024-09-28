from typing import Optional

from fastapi import APIRouter, HTTPException, Cookie, Depends
from fastapi.responses import JSONResponse

from app.core.db.mongo_layer import MongoDBDatabaseLayer
from app.schemas.users import UserResponse, UserCreation
from app.service.user import UserService

router = APIRouter(prefix="/api/user", tags=["user"])


def get_service():
    return UserService(database=MongoDBDatabaseLayer())


def prepare_response(
    content: Optional[dict], token: Optional[str], error: Optional[dict]
) -> JSONResponse:
    if error is not None:
        raise HTTPException(status_code=401, detail=error["detail"])
    response = JSONResponse(content=content)
    response.set_cookie(key="token", value=token)
    return response


@router.post("/login", response_model=UserResponse, status_code=200)
async def login(params: UserCreation, service=Depends(get_service)) -> JSONResponse:
    content, token, error = await service.login(params.dict())
    return prepare_response(content, token, error)


@router.post("/register", response_model=UserResponse, status_code=200)
async def register(params: UserCreation, service=Depends(get_service)) -> JSONResponse:
    content, token, error = await service.create(params.dict())
    return prepare_response(content, token, error)


@router.post("/logout", response_model=bool, status_code=200)
async def logout(
    token: Optional[str] = Cookie(None), service=Depends(get_service)
) -> bool:
    return await service.logout(token)
