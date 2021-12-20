import asyncio
from functools import wraps
from typing import List, Callable, Any

from starlette.websockets import WebSocket

from src.emulations.interfaces import EmuInterface


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, emu: EmuInterface) -> None:
        self.active_connections.remove(websocket)
        emu.stop()

    @staticmethod
    async def send_text(message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    @staticmethod
    async def send_binary(data: bytes, websocket: WebSocket) -> None:
        await websocket.send_bytes(data)

    async def write_to_socket(self, emu: EmuInterface, websocket: WebSocket) -> None:
        response = await emu.receive_console()
        if response is not None:
            await self.send_text(response, websocket)

    async def read_from_socket(self, emu: EmuInterface, websocket: WebSocket) -> None:
        try:
            data = await asyncio.wait_for(websocket.receive(), 0.001)
        except asyncio.exceptions.TimeoutError:
            return

        if data["type"] == "websocket.disconnect":
            self.disconnect(websocket, emu)
            return

        text = data.get("text")
        if text is not None:
            await emu.send_console(text)

    async def check_not_alive(self, emu: EmuInterface, websocket: WebSocket) -> bool:
        if not emu.is_alive():
            try:
                await self.send_text("Your time is out...", websocket)
            except RuntimeError:
                pass
            self.disconnect(websocket, emu)
            return False


manager = ConnectionManager()
