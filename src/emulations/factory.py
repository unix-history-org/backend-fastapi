from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.emulations.interfaces import EmuInterface
from src.emulations.qemu import QEMU
from src.emulations.types import EmuType
from src.emulations.utils.mac_address import random_mac
from src.service.os import OSService
from src.emulations.list_emu import ListEmuSingleton


class EmuFactory(ABC):  # pylint: disable=R0903
    @abstractmethod
    async def create(
        self, emu_type: str, emu_id: str, **parametric
    ) -> Optional[EmuInterface]:
        ...


class QEMUCreation(EmuFactory):  # pylint: disable=R0903
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
            or (
                self.os_from_db["graphics_enable"]
                or self.os_from_db["terminal_enable"]
                and emu_type == "any"
            )
        ):
            return None

        if ListEmuSingleton().find(emu_id) is None:
            return QEMU(self.os_from_db, mac_address=emu_id)

        return ListEmuSingleton().find(emu_id)


async def get_emu(
    os_id: str, emulations_type: str, emu_id: Optional[str | int], **parametric
) -> Optional[EmuInterface]:
    os_from_db = await OSService(os_id, database=MongoDBDatabaseLayer()).get()
    if os_from_db["emulation_type"] == EmuType.QEMU:
        if emu_id is None:
            emu_id = random_mac()
            while ListEmuSingleton().find(emu_id) is not None:
                emu_id = random_mac()
        return await QEMUCreation(os_from_db).create(
            emulations_type, emu_id, **parametric
        )
