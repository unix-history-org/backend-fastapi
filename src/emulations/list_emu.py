from __future__ import annotations

import time
from threading import Lock, Thread

from src.emulations.interfaces import EmuInterface


class ListEmuSingleton:
    _lock: Lock = Lock()
    _list_emu_and_ttl: list = []
    _th = None
    _life_time = 60 * 15  # INFO: 15 минут жизни

    def __init__(self) -> None:
        if self._th is None:
            self._th = Thread(target=ListEmuSingleton._timer, daemon=True)
            self._th.start()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, "instance"):
                cls.instance = super(ListEmuSingleton, cls).__new__(
                    cls, *args, **kwargs
                )
        return cls.instance

    def append(self, emu: EmuInterface) -> None:
        with self._lock:
            self._list_emu_and_ttl.append([emu, self._life_time])

    @classmethod
    def _timer(cls):
        while True:
            with cls._lock:
                for emu_and_ttl in cls._list_emu_and_ttl:
                    emu_and_ttl[1] -= 30
                    if emu_and_ttl[1] < 30:
                        emu_and_ttl[0].stop()
            time.sleep(30)
