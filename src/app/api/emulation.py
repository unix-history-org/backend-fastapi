from fastapi import APIRouter

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.app.schemas.emulation import Emulation
from src.app.schemas.base import MongoID
from src.service.os import OSService

router = APIRouter(
    prefix="/api/emu"
)


@router.get('/start/{os_id}', response_model=Emulation, status_code=200)
async def start_os(os_id: MongoID) -> dict:
    # TODO: Продумать оптимизацию
    service = OSService(os_id, database=MongoDBDatabaseLayer())
    return await service.start_emulation()
