from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.emulations.types import EmuType
from src.service.os import OSService
from src.emulations.qemu import QEMU


class EmuSelector:
    @staticmethod
    async def get_emu(os_id, emu_type, **parametric):
        os = await OSService(os_id, database=MongoDBDatabaseLayer()).get()
        if os["emulation_type"] == EmuType.qemu and (
                os["terminal_enable"] and emu_type == "terminal" or
                os["graphics_enable"] and emu_type == "graphics"
        ):
            return QEMU(os_id, parametric['mac_address'], os=os)
