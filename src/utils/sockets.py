import asyncio
from typing import List

from starlette.websockets import WebSocket, WebSocketState

from src.emulations.interfaces import EmuInterface


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_text(message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    @staticmethod
    async def send_binary(data: bytes, websocket: WebSocket) -> None:
        await websocket.send_bytes(data)

    async def write_to_socket(self, emu: EmuInterface, websocket: WebSocket) -> None:
        if websocket.application_state == WebSocketState.DISCONNECTED:
            emu.stop()
            return

        response = await emu.receive_console()
        if response is not None:
            await self.send_text(response, websocket)

    async def read_from_socket(self, emu: EmuInterface, websocket: WebSocket) -> None:
        if websocket.application_state == WebSocketState.DISCONNECTED:
            emu.stop()
            return

        try:
            data = await asyncio.wait_for(websocket.receive(), 0.1)
        except asyncio.exceptions.TimeoutError:
            return

        if data["type"] == "websocket.disconnect":
            self.disconnect(websocket)
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
            self.disconnect(websocket)
            return True
        return False


manager = ConnectionManager()
