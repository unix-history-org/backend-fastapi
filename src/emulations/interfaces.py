from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class EmuInterface(ABC):
    @abstractmethod
    async def receive_console(self) -> str: ...

    @abstractmethod
    async def send_console(self, data: str): ...

    @abstractmethod
    async def receive_gui(self) -> Optional[bytes | str]: ...

    @abstractmethod
    async def send_gui(self, data: Optional[bytes | str]): ...

    @abstractmethod
    def start_gui(self): ...

    @abstractmethod
    def is_alive(self) -> bool: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def get_id(self) -> UUID: ...

    @abstractmethod
    def get_urls(self) -> dict: ...

    @abstractmethod
    def get_lifetime(self) -> int: ...
