from fastapi import APIRouter, WebSocket

from src.app.schemas.emulation import Emulation
from src.app.schemas.base import MongoID
from src.emulations.factory import get_emu
from src.utils.sockets import manager

router = APIRouter(prefix="/api/emu")


@router.get("/start/{os_id}", response_model=Emulation, status_code=200)
async def start_os(os_id: MongoID) -> dict:
    emu = await get_emu(os_id, emulations_type="any", emu_id=None)
    if emu is None:
        return {}
    return emu.get_urls()


@router.websocket("/api/emu/{os_id}/{emu_id}/cli")  # FastAPI не добавляет префикс
async def cli_ws(websocket: WebSocket, os_id: str, emu_id: str) -> None:
    await manager.connect(websocket)
    emu = await get_emu(os_id, emulations_type="cli", emu_id=emu_id)

    if emu is None:
        return

    await manager.send_text("Running...", websocket)
    while True:
        if await manager.check_not_alive(emu, websocket):
            break

        await manager.write_to_socket(emu, websocket)

        await manager.read_from_socket(emu, websocket)
