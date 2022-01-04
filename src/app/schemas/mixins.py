from pydantic import BaseModel

from src.app.schemas.base import MongoID


class IDModelMixin(BaseModel):  # TODO: Вынести в настройки
    id: MongoID
