from pydantic import BaseModel, Field

from src.app.schemas.base import MongoID


class Token(BaseModel):
    token: str
    user_id: MongoID = Field(alias="userid")


class TokenRequests(BaseModel):
    token: str
