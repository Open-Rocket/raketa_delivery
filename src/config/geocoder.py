import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY_Gogich = os.getenv("YANDEX_API_KEY_Gogich")
YANDEX_API_KEY_Olia = os.getenv("YANDEX_API_KEY_Olia")
YANDEX_API_KEY_Erel = os.getenv("YANDEX_API_KEY_Erel")


__all__ = [
    "YANDEX_API_KEY_Gogich",
    "YANDEX_API_KEY_Olia",
    "YANDEX_API_KEY_Erel",
]
