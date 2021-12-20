from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.emulations.interfaces import EmuInterface
from src.emulations.qemu import QEMU
from src.emulations.types import EmuType
from src.service.os import OSService


class EmuFactory(ABC):
    @abstractmethod
    async def create(
        self, emu_type: str, emu_id: str, **parametric
    ) -> Optional[EmuInterface]:
        ...


class QEMUCreation(EmuFactory):
    def __init__(self, os_from_db: dict):
        self.os_from_db = os_from_db

    async def create(
        self, emu_type: str, emu_id: str, **parametric
    ) -> Optional[EmuInterface]:
        if not (
            self.os_from_db["terminal_enable"]
            and emu_type == "cli"
            or self.os_from_db["graphics_enable"]
            and emu_type == "gui"
        ):
            return None
        return QEMU(self.os_from_db, mac_address=emu_id)


async def get_emu(
    os_id: str, emulations_type: str, emu_id: str, **parametric
) -> Optional[EmuInterface]:
    os_from_db = await OSService(os_id, database=MongoDBDatabaseLayer()).get()
    if os_from_db["emulation_type"] == EmuType.QEMU:
        return await QEMUCreation(os_from_db).create(
            emulations_type, emu_id, **parametric
        )
