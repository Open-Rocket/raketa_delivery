import os
from dotenv import load_dotenv


load_dotenv()

payment_provider = os.getenv("UKASSA_TEST_SHOP")


__all__ = ["payment_provider"]
