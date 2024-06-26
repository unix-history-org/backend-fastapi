from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4, UUID

from src.app.core.db.mongo_layer import MongoDBDatabaseLayer
from src.emulations.interfaces import EmuInterface
from src.emulations.qemu import QEMU
from src.emulations.types import EmuType
from src.service.os import OSService
from src.emulations.list_emu import ListEmuSingleton


class EmuFactory(ABC):  # pylint: disable=R0903
    @abstractmethod
    async def create(
        self, emu_type: str, emu_id: UUID, **parametric
    ) -> Optional[EmuInterface]: ...


class QEMUCreation(EmuFactory):  # pylint: disable=R0903
    def __init__(self, os_from_db: dict):
        self.os_from_db = os_from_db

    async def create(
        self, emu_type: str, emu_id: UUID, **parametric
    ) -> Optional[EmuInterface]:
        if not (
            self.os_from_db["terminal_enable"]
            and emu_type == "cli"
            or self.os_from_db["graphics_enable"]
            and emu_type == "gui"
            or (
                self.os_from_db["graphics_enable"] or self.os_from_db["terminal_enable"]
            )
            and emu_type == "any"
        ):
            return None

        if ListEmuSingleton().find(emu_id) is None:
            return QEMU(self.os_from_db, emu_id)

        return ListEmuSingleton().find(emu_id)


async def get_emu(
    os_id: Optional[str], emulations_type: str, emu_id: Optional[UUID], **parametric
) -> Optional[EmuInterface]:
    if emu_id and not os_id:
        return ListEmuSingleton().find(emu_id)
    os_from_db = await OSService(os_id, database=MongoDBDatabaseLayer()).get()
    if os_from_db["emulation_type"] == EmuType.QEMU:
        if emu_id is None:
            emu_id = uuid4()
            # emu_id = UUID("00000000-0000-0000-0000-000000000000")
        return await QEMUCreation(os_from_db).create(
            emulations_type, emu_id, **parametric
        )
