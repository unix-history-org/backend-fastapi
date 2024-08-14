from enum import IntEnum


class EmuType(IntEnum):
    DISABLE = -1
    QEMU = 0
    PDP11 = 1


class GraphicalTypes(IntEnum):
    IFRAME = 0
    WEBSOCKET = 1
