import random
from typing import Optional

from src.app.core.db.base_layer import AbstractDatabaseLayer
from src.emulations.utils.mac_address import random_mac
from src.service.base import BaseService
from src.service.mixins import ServiceCRUDMixin
from src.settings import settings


class OSService(ServiceCRUDMixin, BaseService):
    def __init__(
        self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer
    ) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = "os"

    async def start_emulation(self) -> dict:
        mac_address = random_mac()
        os_obj = await self.get()
        ret = {}
        if os_obj["terminal_enable"]:
            ret |= {
                "terminal": f"{settings.WEBSOCKET_TYPE}://{settings.BASE_URL}/api/emu/{self.obj_id}/{mac_address}/cli"
            }
        if os_obj["graphics_enable"]:
            ret |= {"graphical": f"{settings.WEBSOCKET_TYPE}://{settings.BASE_URL}/"}
        return ret
