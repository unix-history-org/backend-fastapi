from abc import ABC, abstractmethod
from typing import Optional

from src.app.core.db.base_layer import AbstractDatabaseLayer


class BaseService(ABC):
    model_name: str = None  # Переопределяется в наследника

    def __init__(self, obj_id: Optional[str] = None,  *, database: AbstractDatabaseLayer) -> None:
        self.database = database
        self.obj_id = obj_id
        self.id_key = '_id'

    @abstractmethod
    async def get(self, *args, **kwargs):
        ...

    @abstractmethod
    async def create(self, params):
        ...

    @abstractmethod
    async def update(self, params: dict) -> dict:
        ...

    @abstractmethod
    async def remove(self):
        ...

    def _append_id_object(self, obj):
        if obj is None:
            return None

        obj_id = {'id': str(obj.pop(self.id_key, 'none'))}  # noqa: Это миксин для сервисов,
        # а id_key определён в базов классе

        return obj | obj_id

    def _append_id_to_list(self, objs):
        if objs is None:
            return None

        ret_objs = []

        for obj in objs:
            ret_objs.append(self._append_id_object(obj))

        return ret_objs
