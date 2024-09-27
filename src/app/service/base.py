from abc import ABC, abstractmethod
from typing import Optional

from app.core.db.base_layer import AbstractDatabaseLayer


class BaseService(ABC):
    model_name: str = None  # Переопределяется в наследника

    def __init__(
        self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer
    ) -> None:
        self.database = database
        self.obj_id = obj_id

    @abstractmethod
    async def get(self, *args, **kwargs) -> dict | list: ...

    @abstractmethod
    async def create(self, params: dict) -> dict: ...

    @abstractmethod
    async def update(self, params: dict) -> dict: ...

    @abstractmethod
    async def remove(self) -> bool: ...
