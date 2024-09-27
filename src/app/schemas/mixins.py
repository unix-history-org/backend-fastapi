from pydantic import BaseModel

from app.schemas.base import MongoID


class IDModelMixin(BaseModel):
    id: MongoID
