import random


def random_mac() -> str:
    # Первые три байта - производитель, у нас QEMU
    return ":".join(
        map(
            lambda x: f"{x:02x}",
            [
                0x52,
                0x54,
                0x00,
                random.randint(0x00, 0xFF),
                random.randint(0x00, 0xFF),
                random.randint(0x00, 0xFF),
            ],
        )
    )
