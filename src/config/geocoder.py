from ._deps import os, load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")


__all__ = ["YANDEX_API_KEY"]
