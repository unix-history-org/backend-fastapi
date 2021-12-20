from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Optional,
)


class AbstractDatabaseLayer(ABC):
    @abstractmethod
    async def get(self, name: str, filters: dict) -> Optional[dict]:
        ...

    @abstractmethod
    async def get_all(self, name: str) -> Optional[list]:
        ...

    @abstractmethod
    async def first(self, name: str) -> Optional[dict]:
        ...

    @abstractmethod
    async def create(self, name: str, params: dict) -> dict:
        ...

    @abstractmethod
    async def update(self, name: str, filters: dict, params: dict) -> Optional[dict]:
        ...

    @abstractmethod
    async def delete(self, name: str, filters: dict) -> bool:
        ...

    @abstractmethod
    async def count(self, name: str, filters: dict) -> int:
        ...

    @abstractmethod
    async def exists(self, name: str, filters: dict) -> bool:
        ...
