import os
from dotenv import load_dotenv


load_dotenv()

payment_provider = os.getenv("UKASSA_LIVE")


__all__ = ["payment_provider"]
