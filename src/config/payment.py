import os
from dotenv import load_dotenv


load_dotenv()

payment_provider = os.getenv("UKASSA_TEST")


__all__ = ["payment_provider"]
