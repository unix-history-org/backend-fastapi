import asyncio
import functools
import logging
import os
import subprocess
import multiprocessing
from io import StringIO
from shutil import copy
from queue import Queue, Empty
from threading import Thread
from typing import Optional
from uuid import UUID
import websockets
from websockify.websocketproxy import WebSocketProxy

from app.emulations.interfaces import EmuInterface
from app.emulations.list_emu import ListEmuSingleton
from app.emulations.types import GraphicalTypes
from settings import settings

NOVNC_DEFAULT_PORT = 6080
VNC_DEFAULT_PORT = 5900
KILL_SIGNAL_NUM = 9


def _retry_decorator(func):
    @functools.wraps(func)
    async def _wrapper(*args, **kwargs):
        retries = 3
        delay = 1
        error = None
        for _ in range(retries):
            try:
                return await func(*args, **kwargs)
            except OSError as e:
                error = e
                await asyncio.sleep(delay)
        raise error

    return _wrapper


class _WebsockifyProxyWithLogger(WebSocketProxy):  # pylint: disable=R0903
    def __init__(self, *args, **kwargs):
        self._logger = kwargs.pop("logger")
        self._logger_name = kwargs.pop("logger_name")
        super().__init__(*args, **kwargs)

    def get_logger(self):
        return self._logger

    @staticmethod
    def create_and_run(*args, **kwargs):
        _WebsockifyProxyWithLogger(*args, **kwargs).start_server()


class _GuiSocketHelper:  # pylint: disable=R0903
    def __init__(
        self, url: str, input_queue: asyncio.Queue, output_queue: asyncio.Queue
    ):
        self._url = url
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._websocket = None
        self._stop = False
        loop = asyncio.get_event_loop()
        loop.create_task(self._connect())

    def stop(self):
        self._stop = True

    @_retry_decorator
    async def _connect(self):
        async with websockets.connect(self._url) as websocket:
            self._websocket = websocket
            read_task = asyncio.create_task(self._read_messages())
            write_task = asyncio.create_task(self._write_messages())
            _, pending = await asyncio.wait(
                [read_task, write_task], return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()

    async def _read_messages(self):
        try:
            async for message in self._websocket:
                if self._stop:
                    break
                await self._output_queue.put(message)
        except asyncio.exceptions.IncompleteReadError:
            ...
        except websockets.exceptions.ConnectionClosedError:
            ...

    async def _write_messages(self):
        while not self._stop:
            message = await self._input_queue.get()
            await self._websocket.send(message)
            self._input_queue.task_done()


class QEMU(EmuInterface):  # pylint: disable=R0902

    _used_port = []
    _alive = True
    _reading = True
    _fifo_name: str = None
    _disk_path: str = None
    _websockify_process: Optional[multiprocessing.Process] = None
    _queue: Queue = None
    _read_console_thread: Thread = None
    _qemu: Optional[subprocess.Popen] = None
    _vnc_port: int = None
    _gui_socket_helper: Optional[_GuiSocketHelper] = None
    _gui_helper_input_queue: Optional[asyncio.Queue] = None
    _gui_helper_output_queue: Optional[asyncio.Queue] = None

    def __init__(self, os_from_db: dict, emu_id: Optional[UUID]) -> None:
        self._tmp_dir_name = "/tmp/unix-history"
        self._uuid = emu_id
        self._os = os_from_db

        self._create_tmp_dir()
        self._make_fifo()
        self._copy_disk()
        self._vnc_port = self._get_next_port()
        command = self._get_command()

        self._run_console_threads()
        self._logger = logging.getLogger(f"QEMU_{emu_id}")

        self._qemu = subprocess.Popen(command.split(" "))  # pylint: disable=R1732

        ListEmuSingleton().append(self)

    def __del__(self) -> None:
        self.stop()

    def start_gui(self):
        if self._os.get("graphics_enable"):
            self._websockify_stop()
            self._websockify_init()

    def get_lifetime(self) -> int:
        return self._os.get("lifetime", 60 * 15)

    def get_id(self) -> UUID:
        return self._uuid

    def get_urls(self) -> dict:
        ret = {"emulation_id": self.get_id()}
        if self._os["terminal_enable"]:
            ret |= {
                "terminal": f"api/emu/{self._os['id']}/{self.get_id()}/cli"
            }
        if self._os["graphics_enable"]:
            # INFO: PROXYING ON NGINX SIDE
            ret |= {
                "graphical": f"api/emu/{self._os['id']}/{self.get_id()}/gui"
            }
            ret |= {"graphical_type": GraphicalTypes.IFRAME}
        return ret

    async def receive_console(self) -> str:
        size = self._queue.qsize()
        res = StringIO()
        for _ in range(size):  # Для оптимизации
            if el := self._get_element():
                res.write(el)
                continue
            break
        return res.getvalue()

    async def send_console(self, data: str) -> None:
        with open(f"{self._fifo_name}.in", "w", encoding="UTF-8") as inp:
            inp.write(data)

    async def receive_gui(self) -> Optional[bytes | str]:
        if self._gui_socket_helper is not None:
            try:
                return self._gui_helper_output_queue.get_nowait()
            except asyncio.QueueEmpty:
                ...

    async def send_gui(self, data: Optional[bytes | str]) -> None:
        if self._gui_socket_helper is not None:
            self._gui_helper_input_queue.put_nowait(data)

    def stop(self) -> None:
        self._kill_subprocess_and_thread()
        self._delete_files()
        self._alive = False
        ListEmuSingleton().remove(self.get_id())

    def is_alive(self) -> bool:
        return self._alive

    def _websockify_init(self):
        self._websockify_process = multiprocessing.Process(
            target=_WebsockifyProxyWithLogger.create_and_run,
            kwargs={
                "target_host": "localhost",
                "target_port": VNC_DEFAULT_PORT + self._vnc_port,
                "listen_host": "0.0.0.0",
                "listen_port": NOVNC_DEFAULT_PORT + self._vnc_port,
                "logger": logging.getLogger(f"WEBSOCKIFY_{self.get_id()}"),
                "logger_name": f"WEBSOCKIFY_{self.get_id()}",
            },
            daemon=False,
        )
        self._websockify_process.start()
        self._gui_helper_input_queue = asyncio.Queue()
        self._gui_helper_output_queue = asyncio.Queue()
        self._gui_socket_helper = _GuiSocketHelper(
            f"ws://localhost:{NOVNC_DEFAULT_PORT + self._vnc_port}/websockify",
            input_queue=self._gui_helper_input_queue,
            output_queue=self._gui_helper_output_queue,
        )

    def _websockify_stop(self):
        if self._gui_socket_helper:
            self._gui_socket_helper.stop()
        if self._websockify_process:
            self._websockify_process.kill()
        self._websockify_process = None

        self._gui_socket_helper = None
        self._gui_helper_input_queue = None
        self._gui_helper_output_queue = None

    def _run_console_threads(self):
        self._queue = Queue()
        self._read_console_thread = Thread(
            target=QEMU._thread_console_reading, args=(self,), daemon=True
        )
        self._read_console_thread.start()

    def _get_command(self):
        return self._os["start_config"].format(
            fifo=self._fifo_name,
            disk_path=self._disk_path,
            port=self._vnc_port,
            name=self._uuid,
        )

    async def _connect(self):
        return await websockets.connect(
            f"ws://localhost:{NOVNC_DEFAULT_PORT + self._vnc_port}/websockify"
        )

    def _make_fifo(self) -> None:
        self._fifo_name = f"{self._tmp_dir_name}/{self._uuid}"
        try:
            os.remove(self._fifo_name + ".in")
            os.remove(self._fifo_name + ".out")
        except FileNotFoundError:
            pass
        os.mkfifo(self._fifo_name + ".in")
        os.mkfifo(self._fifo_name + ".out")

    def _copy_disk(self) -> None:
        self._disk_path = (
            f"{self._tmp_dir_name}/"
            f"{self._replace_os_name(self._os['name'])}"
            f"_{self._uuid}.img"
        )
        try:
            os.remove(self._disk_path)
        except FileNotFoundError:
            pass
        copy(self._os["template_disk_path"], self._disk_path)

    def _thread_console_reading(self) -> None:
        with open(f"{self._fifo_name}.out", "r", encoding="UTF-8") as out:
            while self._reading:
                data = out.read(1)
                if data == "\n":
                    data += "\r"
                self._queue.put_nowait(data)

    def _get_element(self) -> Optional[str]:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None

    def _delete_files(self) -> None:
        try:
            if self._fifo_name:
                os.remove(self._fifo_name + ".in")
                os.remove(self._fifo_name + ".out")
            if self._disk_path:
                os.remove(self._disk_path)
        except FileNotFoundError:
            pass

    def _kill_subprocess_and_thread(self) -> None:
        if self._qemu is not None:
            self._qemu.send_signal(KILL_SIGNAL_NUM)
            self._qemu = None
        if self._websockify_process is not None:
            self._websockify_process.kill()

        self._reading = False
        if self._vnc_port in self._used_port:
            self._used_port.remove(self._vnc_port)

    def _create_tmp_dir(self):
        os.makedirs(self._tmp_dir_name, exist_ok=True)

    @classmethod
    def _get_next_port(cls) -> int:
        if not cls._used_port:
            cls._used_port.append(1)
            return 1

        port = cls._used_port[-1] + 1
        cls._used_port.append(port)
        return port

    @staticmethod
    def _replace_os_name(os_name: str) -> str:
        return os_name.replace(" ", "_")
