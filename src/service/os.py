import random
from typing import Optional

from src.app.core.db.base_layer import AbstractDatabaseLayer
from src.service.base import BaseService
from src.service.mixins import ServiceCRUDMixin
from src.settings import Settings


class OSService(ServiceCRUDMixin, BaseService):
    def __init__(self, obj_id: Optional[str] = None, *, database: AbstractDatabaseLayer) -> None:
        super().__init__(obj_id, database=database)
        self.model_name = 'os'

    async def start_emulation(self) -> dict:
        mac_address = self.random_mac()
        return {
            "terminal": f"ws://{Settings.BASE_URL}/api/emu/{self.obj_id}/{mac_address}/cli",
            "graphical": f"ws://{Settings.BASE_URL}/"
        }

    @staticmethod
    def random_mac(emu_type="qemu"):
        mac_prefix = {'xen': [0x00, 0x16, 0x3E], 'qemu': [0x52, 0x54, 0x00]}

        try:
            mac = mac_prefix[emu_type]
        except KeyError:
            mac = mac_prefix['xen']

        mac = mac + [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)]
        ret_mac = ':'.join(map(lambda x: "%02x" % x, mac))
        return ret_mac
