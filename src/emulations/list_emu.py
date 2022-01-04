from __future__ import annotations

import time
from threading import Lock, Thread
from typing import Optional

from src.emulations.interfaces import EmuInterface


class ListEmuSingleton:
    _lock: Lock = Lock()
    _list_emu_and_ttl_and_id: list = []
    _th = None
    _life_time = 60 * 15  # INFO: 15 минут жизни

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
            self._list_emu_and_ttl_and_id.append([emu, self._life_time, emu.get_id()])

    def find(self, _id: str | int) -> Optional[EmuInterface]:
        for emu_and_ttl_and_id in self._list_emu_and_ttl_and_id:
            emu, _, emu_id = emu_and_ttl_and_id
            if emu_id == _id:
                return emu
        return None

    @classmethod
    def _timer(cls) -> None:
        while True:
            emu_stop_list = []
            with cls._lock:
                for emu_and_ttl_and_id in cls._list_emu_and_ttl_and_id:
                    emu_and_ttl_and_id[1] -= 30
                    if emu_and_ttl_and_id[1] < 30:
                        emu_stop_list.append(emu_and_ttl_and_id[0])
                        cls._list_emu_and_ttl_and_id.remove(emu_and_ttl_and_id)
            cls.__stop_for_list(emu_stop_list)
            time.sleep(30)

    @staticmethod
    def __stop_for_list(list_stooped: list) -> None:
        for emu in list_stooped:
            emu.stop()
