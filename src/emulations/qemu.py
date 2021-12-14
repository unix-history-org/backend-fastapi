import os
import subprocess
from shutil import copy
from queue import Queue, Empty
from threading import Thread

from src.emulations.base import BaseEmu

from websocket import WebSocket

NOVNC_DEFAULT_PORT = 6080
VNC_DEFAULT_PORT = 5900


class QEMU(BaseEmu):
    _used_port = []

    def __init__(self, os_id: str, mac_address: str, **parametric):
        super().__init__(**parametric)
        self.os_id = os_id
        self.mac_address = mac_address
        self.os = parametric["os"]

        self.fifo_name = f"/tmp/unix-history/{self.mac_address.replace(':', '_')}"
        self.mkfifo()

        self.disk_template_name = self.os["template_disk_path"]
        self.disk_name = f"/tmp/unix-history/{self.os['name']}_{self.mac_address}.img"
        self.copy_disk()

        self.vnc_port = self.get_next_port()
        self.command = self.os["start_config"].format(
            mac_address=self.mac_address,
            fifo=self.fifo_name,
            disk_path=self.disk_name,
            port=self.vnc_port,
        )

        self.queue = Queue()
        self.read_thread = Thread(
            target=QEMU.thread_reading,
            args=(self.fifo_name, self.queue),
            daemon=True
        )
        self.read_thread.start()

        self.qemu = subprocess.Popen(self.command.split(' '))

        self.novnc_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.novnc = subprocess.Popen(
            (
                f"{self.novnc_path}/noVNC/utils/novnc_proxy "
                f"--vnc localhost:{VNC_DEFAULT_PORT + self.vnc_port} "
                f"--listen {NOVNC_DEFAULT_PORT + self.vnc_port}"
            ).split(' ')
        )

    @classmethod
    def get_next_port(cls):
        if not cls._used_port:
            cls._used_port.append(1)
            return 1
        else:
            port = cls._used_port[-1] + 1
            cls._used_port.append(port)
            return port

    def mkfifo(self):
        try:
            os.remove(self.fifo_name + ".in")
            os.remove(self.fifo_name + ".out")
        except FileNotFoundError:
            pass
        os.mkfifo(self.fifo_name + ".in")
        os.mkfifo(self.fifo_name + ".out")

    def copy_disk(self):
        try:
            os.remove(self.disk_name)
        except FileNotFoundError:
            pass
        copy(self.disk_template_name, self.disk_name)

    @staticmethod
    def thread_reading(fifo_name, queue):
        out = open(f"{fifo_name}.out", "r")
        while True:
            queue.put(out.read(1))

    async def receive_console(self):
        try:
            line = self.queue.get_nowait()
        except Empty:
            pass
        else:
            return line

    async def send_console(self, data):
        with open(f"{self.fifo_name}.in", "w") as inp:
            inp.writelines(data)

    async def receive_gui(self):
        ...

    async def send_gui(self, data):
        ...

    def stop(self):
        self.qemu.kill()
        self.qemu = None
        self._used_port.remove(self.vnc_port)
        self.novnc.kill()
        self.read_thread._stop()
        try:
            os.remove(self.fifo_name + ".in")
            os.remove(self.fifo_name + ".out")
            os.remove(self.disk_name)
        except FileNotFoundError:
            pass
        super().stop()

    def __del__(self):
        self.stop()
