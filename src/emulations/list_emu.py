from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock, Thread
from typing import Optional
from uuid import UUID

from src.emulations.interfaces import EmuInterface

_STOP_STEP = 30


@dataclass
class _EmuControl:
    emu: EmuInterface
    lifetime: int
    emu_id: UUID


class ListEmuSingleton:
    _lock: Lock = Lock()
    _dict_emu_and_ttl_and_id: dict[UUID, _EmuControl] = {}
    _th = None

    def __init__(self) -> None:
        if self._th is None:
            self._th = Thread(target=ListEmuSingleton._timer, daemon=True)
            self._th.start()

    def __new__(cls, *args, **kwargs) -> ListEmuSingleton:
        with cls._lock:
            if not hasattr(cls, "instance"):
                cls.instance = super(ListEmuSingleton, cls).__new__(
                    cls, *args, **kwargs
                )
        return cls.instance

    def append(self, emu: EmuInterface) -> None:
        with self._lock:
            self._dict_emu_and_ttl_and_id[emu.get_id()] = _EmuControl(
                emu=emu, lifetime=emu.get_lifetime(), emu_id=emu.get_id()
            )

    def find(self, _id: UUID) -> Optional[EmuInterface]:  # pylint: disable=R1710
        if emu_control := self._dict_emu_and_ttl_and_id.get(_id):
            return emu_control.emu

    def remove(self, _id: UUID):
        self._dict_emu_and_ttl_and_id.pop(_id)

    @classmethod
    def _timer(cls) -> None:
        while True:
            emu_stop_list = []
            with cls._lock:
                for emu_and_ttl_and_id in cls._dict_emu_and_ttl_and_id.values():
                    emu_and_ttl_and_id.lifetime -= _STOP_STEP
                    if emu_and_ttl_and_id.lifetime < _STOP_STEP:
                        emu_stop_list.append(emu_and_ttl_and_id[0])
                        cls._dict_emu_and_ttl_and_id.pop(emu_and_ttl_and_id.emu_id)
            cls.__stop_for_list(emu_stop_list)
            time.sleep(_STOP_STEP)

    @staticmethod
    def __stop_for_list(list_stooped: list) -> None:
        for emu in list_stooped:
            emu.stop()
