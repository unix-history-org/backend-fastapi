import asyncio
from uuid import UUID

from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect
from websockets import ConnectionClosed

from app.schemas.emulation import Emulation
from app.schemas.base import MongoID
from app.emulations.factory import get_emu
from utils.sockets import manager
from utils.stoppable_thread import StoppableThread

router = APIRouter(prefix="/api/emu", tags=["emulation"])


@router.get("/start/{os_id}", response_model=Emulation, status_code=200)
async def start_os(os_id: MongoID) -> dict:
    emu = await get_emu(os_id, emulations_type="any", emu_id=None)
    if emu is None:
        raise HTTPException(status_code=404, detail="Невозможно запустить эмуляцию")
    return emu.get_urls()


@router.get("/stop/{emu_id}", status_code=200)
async def stop_os(emu_id: UUID) -> bool:
    emu = await get_emu(None, emulations_type="any", emu_id=emu_id)
    if emu is not None:
        emu.stop()
    return True


@router.websocket("/{os_id}/{emu_id}/cli")
async def cli_ws(websocket: WebSocket, os_id: str, emu_id: UUID) -> None:
    print(f"websocket {os_id}/{emu_id}/cli")
    await manager.connect(websocket)
    emu = await get_emu(os_id, emulations_type="cli", emu_id=emu_id)

    if emu is None:
        return

    await manager.send_text("Running...\n\n\r", websocket)
    thread = StoppableThread(
        target=asyncio.new_event_loop().run_until_complete,
        args=(
            asyncio.wait(
                [
                    asyncio.create_task(manager.write_text_to_socket(emu, websocket)),
                    asyncio.create_task(manager.read_text_from_socket(emu, websocket)),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            ),
        ),
    )
    try:
        thread.start()
        while True:
            await asyncio.sleep(0)
    except (ConnectionClosed, WebSocketDisconnect, RuntimeError):
        ...

    emu.stop()
    thread.stop()


@router.websocket("/{os_id}/{emu_id}/gui")
async def gui_ws(websocket: WebSocket, os_id: str, emu_id: UUID) -> None:
    print(f"websocket {os_id}/{emu_id}/gui")
    await manager.connect(websocket)
    emu = await get_emu(os_id, emulations_type="gui", emu_id=emu_id)

    if emu is None:
        return

    emu.start_gui()

    thread = StoppableThread(
        target=asyncio.new_event_loop().run_until_complete,
        args=(
            asyncio.wait(
                [
                    asyncio.create_task(manager.write_gui_to_socket(emu, websocket)),
                    asyncio.create_task(manager.read_gui_from_socket(emu, websocket)),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            ),
        ),
    )
    try:
        thread.start()
        while True:
            await asyncio.sleep(0)
    except (ConnectionClosed, WebSocketDisconnect, RuntimeError):
        ...

    emu.stop()
    thread.stop()
