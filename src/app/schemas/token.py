from pydantic import BaseModel

from src.app.schemas.base import MongoID


class Token(BaseModel):
    token: str
    user_id: MongoID


class TokenRequests(BaseModel):
    token: str
