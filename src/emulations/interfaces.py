from __future__ import annotations

from abc import ABC, abstractmethod


class EmuInterface(ABC):
    @abstractmethod
    async def receive_console(self) -> str:
        ...

    @abstractmethod
    async def send_console(self, data: str):
        ...

    @abstractmethod
    async def receive_gui(self) -> bytes:
        ...

    @abstractmethod
    async def send_gui(self, data: bytes):
        ...

    @abstractmethod
    def is_alive(self) -> bool:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...
