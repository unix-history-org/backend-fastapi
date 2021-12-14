import asyncio
from typing import List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Cookie
from starlette.endpoints import WebSocketEndpoint

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.app.schemas.emulation import Emulation
from src.app.schemas.base import MongoID
from src.emulations.base import BaseEmu
from src.emulations.selector import EmuSelector
from src.service.os import OSService

router = APIRouter(
    prefix="/api/emu"
)


@router.get('/start/{os_id}', response_model=Emulation, status_code=200)
async def start_os(os_id: MongoID) -> dict:
    # TODO: Продумать оптимизацию
    service = OSService(os_id, database=MongoDBDatabaseLayer())
    return await service.start_emulation()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, emu: BaseEmu):
        self.active_connections.remove(websocket)
        emu.stop()

    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_binary(self, data, websocket: WebSocket):
        await websocket.send_bytes(data)


manager = ConnectionManager()


@router.websocket('/api/emu/{os_id}/{mac_address}/cli')  # TODO: FastAPI не добавляет префикс
async def cli_ws(
        websocket: WebSocket,
        os_id: str,
        mac_address: str
):
    await manager.connect(websocket)
    emu = await EmuSelector.get_emu(os_id, emu_type="terminal", mac_address=mac_address)

    if emu is not None:
        await manager.send_text("Running...", websocket)
        while True:
            if not emu.is_alive():
                try:
                    await manager.send_text("Your time is out...", websocket)
                except RuntimeError:
                    pass
                manager.disconnect(websocket, emu)
                break

            response = await emu.receive_console()
            if response is not None:
                await manager.send_text(response, websocket)

            try:
                data = await asyncio.wait_for(websocket.receive(), 0.01)
            except asyncio.exceptions.TimeoutError:
                pass
            else:
                if data["type"] == "websocket.disconnect":
                    manager.disconnect(websocket, emu)
                    break
                text = data.get('text')
                if text is not None:
                    await emu.send_console(text)

# TODO: Продумать как прокинуть noVNC через мои сокеты
