from enum import IntEnum


class EmuType(IntEnum):
    disable = -1
    qemu = 0
    pdp11 = 1
