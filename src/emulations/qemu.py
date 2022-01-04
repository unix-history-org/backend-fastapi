import os
import subprocess
from shutil import copy
from queue import Queue, Empty
from threading import Thread

from src.emulations.interfaces import EmuInterface
from src.emulations.list_emu import ListEmuSingleton
from src.emulations.types import GraphicalTypes
from src.settings import settings

NOVNC_DEFAULT_PORT = 6080
VNC_DEFAULT_PORT = 5900
KILL_SIGNAL_NUM = 9


class QEMU(EmuInterface):  # pylint: disable=R0902
    _used_port = []

    def __init__(self, os_from_db: dict, mac_address: str) -> None:
        """
        В Качестве id используется mac адрес
        """
        self._alive = True
        self._reading = True
        self._mac_address = mac_address

        ListEmuSingleton().append(self)

        self._os = os_from_db

        self._fifo_name = f"/tmp/unix-history/{self._mac_address.replace(':', '_')}"
        self._make_fifo()

        self._disk_path = (
            f"/tmp/unix-history/{self._os['name']}_{self._mac_address}.img"
        )
        self._copy_disk()

        self._vnc_port = self._get_next_port()
        command = self._os["start_config"].format(
            mac_address=self._mac_address,
            fifo=self._fifo_name,
            disk_path=self._disk_path,
            port=self._vnc_port,
        )

        self._queue = Queue()
        self._read_thread = Thread(
            target=QEMU._thread_reading, args=(self,), daemon=True
        )
        self._read_thread.start()

        self._qemu = subprocess.Popen(command.split(" "))  # pylint: disable=R1732

        novnc_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        self._novnc = subprocess.Popen(  # pylint: disable=R1732
            (
                f"{novnc_path}/noVNC/utils/novnc_proxy "
                f"--vnc localhost:{VNC_DEFAULT_PORT + self._vnc_port} "
                f"--listen {NOVNC_DEFAULT_PORT + self._vnc_port}"
            ).split(" ")
        )

    def get_id(self) -> str | int:
        return self._mac_address

    def get_urls(self) -> dict:
        ret = {}
        if self._os["terminal_enable"]:
            ret |= {
                "terminal": f"{settings.WEBSOCKET_TYPE}://{settings.BASE_URL}/"
                f"api/emu/{self._os['id']}/{self.get_id()}/cli"
            }
        if self._os["graphics_enable"]:
            # INFO: PROXYING ON NGINX SIDE
            ret |= {
                "graphical": f"{settings.HTTP_OR_HTTPS}://{settings.BASE_URL}/"
                f"novnc/{NOVNC_DEFAULT_PORT + self._vnc_port}/"
            }
            ret |= {"graphical_type": GraphicalTypes.IFRAME}
        return ret

    @classmethod
    def _get_next_port(cls) -> int:
        if not cls._used_port:
            cls._used_port.append(1)
            return 1

        port = cls._used_port[-1] + 1
        cls._used_port.append(port)
        return port

    def _make_fifo(self) -> None:
        try:
            os.remove(self._fifo_name + ".in")
            os.remove(self._fifo_name + ".out")
        except FileNotFoundError:
            pass
        os.mkfifo(self._fifo_name + ".in")
        os.mkfifo(self._fifo_name + ".out")

    def _copy_disk(self) -> None:
        try:
            os.remove(self._disk_path)
        except FileNotFoundError:
            pass
        copy(self._os["template_disk_path"], self._disk_path)

    def _thread_reading(self) -> None:
        out = open(  # pylint: disable=R1732
            f"{self._fifo_name}.out", "r", encoding="UTF-8"
        )
        while self._reading:
            self._queue.put(out.read(1))

    async def receive_console(self) -> str:
        try:
            return self._queue.get_nowait()
        except Empty:
            pass

    async def send_console(self, data: str) -> None:
        with open(f"{self._fifo_name}.in", "w", encoding="UTF-8") as inp:
            inp.writelines(data)

    async def receive_gui(self) -> bytes:
        raise NotImplementedError()

    async def send_gui(self, data: bytes) -> None:
        raise NotImplementedError()

    def _delete_files(self) -> None:
        try:
            os.remove(self._fifo_name + ".in")
            os.remove(self._fifo_name + ".out")
            os.remove(self._disk_path)
        except FileNotFoundError:
            pass

    def _kill_subprocess_and_thread(self) -> None:
        if self._qemu is not None:
            self._qemu.send_signal(KILL_SIGNAL_NUM)
            self._qemu = None
        if self._novnc is not None:
            ps_output = subprocess.run(  # pylint: disable=W1510
                ["ps", "-opid", "--no-headers", "--ppid", str(self._novnc.pid)],
                stdout=subprocess.PIPE,
                encoding="utf8",
            )
            for line in ps_output.stdout.splitlines():
                subprocess.run(  # pylint: disable=W1510
                    ["kill", f"-{KILL_SIGNAL_NUM}", line]
                )
            self._novnc.send_signal(KILL_SIGNAL_NUM)
            self._novnc = None

        self._reading = False
        if self._vnc_port in self._used_port:
            self._used_port.remove(self._vnc_port)

    def stop(self) -> None:
        self._kill_subprocess_and_thread()
        self._delete_files()
        self._alive = False

    def is_alive(self) -> bool:
        return self._alive

    def __del__(self) -> None:
        self.stop()
