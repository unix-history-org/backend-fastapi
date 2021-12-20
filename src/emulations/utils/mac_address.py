import random


def random_mac() -> str:
    mac_prefix = [0x52, 0x54, 0x00]

    mac = mac_prefix

    mac += [
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
    ]
    return ":".join(map(lambda x: "%02x" % x, mac))
