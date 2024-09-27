import asyncio
from typing import List

from starlette.websockets import WebSocket

from app.emulations.interfaces import EmuInterface


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_text(message: str, websocket: WebSocket, ping: bool = False) -> None:
        if not ping:
            await websocket.send_text(f"0:{message}")
        else:
            await websocket.send_text("1:pong")

    @staticmethod
    async def send_binary(data: bytes, websocket: WebSocket) -> None:
        await websocket.send_bytes(data)

    @staticmethod
    async def write_gui_to_socket(emu: EmuInterface, websocket: WebSocket):
        while True:
            response = await emu.receive_gui()
            if response is not None:
                if isinstance(response, str):
                    await websocket.send_text(response)
                if isinstance(response, bytes):
                    await websocket.send_bytes(response)
            await asyncio.sleep(0)

    async def read_gui_from_socket(self, emu: EmuInterface, websocket: WebSocket):
        async for message in websocket.iter_bytes():
            await emu.send_gui(message)
        self.disconnect(websocket)

    async def write_text_to_socket(
        self, emu: EmuInterface, websocket: WebSocket
    ) -> None:
        while True:
            response = await emu.receive_console()
            if response is not None:
                await self.send_text(response, websocket)
            await asyncio.sleep(0)

    async def read_text_from_socket(
        self, emu: EmuInterface, websocket: WebSocket
    ) -> None:
        async for text in websocket.iter_text():
            if await self.check_not_alive(emu, websocket):
                break
            if text.startswith("1:"):
                await self.send_text("", websocket, ping=True)
                continue

            await emu.send_console(text[2:])

        self.disconnect(websocket)

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
