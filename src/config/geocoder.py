import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_API_KEY_2 = os.getenv("YANDEX_API_KEY_2")


__all__ = [
    "YANDEX_API_KEY",
    "YANDEX_API_KEY_2",
]
