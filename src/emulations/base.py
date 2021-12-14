import time
from abc import ABC, abstractmethod

from threading import Lock, Thread


class BaseEmu(ABC):
    def __init__(self, **parametric):
        ListEmuSingleton().append(self)
        self.alive = True

    @abstractmethod
    async def receive_console(self):
        ...

    @abstractmethod
    async def send_console(self, data):
        ...

    @abstractmethod
    async def receive_gui(self):
        ...

    @abstractmethod
    async def send_gui(self, data):
        ...

    def stop(self):
        self.alive = False

    def is_alive(self):
        return self.alive


class ListEmuSingleton:
    _lock: Lock = Lock()

    _list: list = []
    _th = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(ListEmuSingleton, cls).__new__(cls, *args, **kwargs)
            cls._th = Thread(target=ListEmuSingleton.timer, daemon=True)
            cls._th.start()
        return cls.instance

    def append(self, emu: BaseEmu) -> None:
        life_time = 60*15  # INFO: 15 минут жизни
        with self._lock:
            self._list.append([emu, life_time])

    @classmethod
    def timer(cls):
        with cls._lock:
            for emu in cls._list:
                emu[1] -= 30
                if emu[1] < 30:
                    emu[0].stop()
        time.sleep(30)
