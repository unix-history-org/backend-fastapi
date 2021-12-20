import os
import subprocess
from shutil import copy
from queue import Queue, Empty
from threading import Thread

from src.emulations.interfaces import EmuInterface
from src.emulations.list_emu import ListEmuSingleton


NOVNC_DEFAULT_PORT = 6080
VNC_DEFAULT_PORT = 5900


class QEMU(EmuInterface):
    _used_port = []

    def __init__(self, os_from_db: dict, mac_address: str) -> None:
        """
        В Качестве id используется mac адрес
        """
        self._alive = True
        ListEmuSingleton().append(self)

        self._mac_address = mac_address
        self._os = os_from_db

        self._fifo_name = f"/tmp/unix-history/{self._mac_address.replace(':', '_')}"
        self._make_fifo()

        self._disk_path = (
            f"/tmp/unix-history/{self._os['name']}_{self._mac_address}.img"
        )
        self._copy_disk()

        self._vnc_port = self._get_next_port()
        self._command = self._os["start_config"].format(
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

        self._qemu = subprocess.Popen(self._command.split(" "))

        self._novnc_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        self._novnc = subprocess.Popen(
            (
                f"{self._novnc_path}/noVNC/utils/novnc_proxy "
                f"--vnc localhost:{VNC_DEFAULT_PORT + self._vnc_port} "
                f"--listen {NOVNC_DEFAULT_PORT + self._vnc_port}"
            ).split(" ")
        )

    @classmethod
    def _get_next_port(cls) -> int:
        if not cls._used_port:
            cls._used_port.append(1)
            return 1
        else:
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
        out = open(f"{self._fifo_name}.out", "r")
        while True:
            self._queue.put(out.read(1))

    async def receive_console(self) -> str:
        try:
            return self._queue.get_nowait()
        except Empty:
            pass

    async def send_console(self, data: str):
        with open(f"{self._fifo_name}.in", "w") as inp:
            inp.writelines(data)

    async def receive_gui(self) -> bytes:
        raise NotImplementedError()

    async def send_gui(self, data: bytes):
        raise NotImplementedError()

    def _delete_files(self) -> None:
        try:
            os.remove(self._fifo_name + ".in")
            os.remove(self._fifo_name + ".out")
            os.remove(self._disk_path)
        except FileNotFoundError:
            pass

    def _kill_subprocess_and_thread(self) -> None:
        self._qemu.kill()
        self._qemu = None
        self._novnc.kill()
        self._read_thread._stop()  # noqa
        self._used_port.remove(self._vnc_port)

    def stop(self) -> None:
        self._kill_subprocess_and_thread()
        self._delete_files()
        self._alive = False

    def is_alive(self) -> bool:
        return self._alive

    def __del__(self) -> None:
        self.stop()
