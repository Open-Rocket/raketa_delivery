from dependencies._dependencies import os, Bot, Dispatcher, load_dotenv

load_dotenv()

customer_bot = Bot(token=os.getenv("CUSTOMER_BOT"))
couriers_bot = Bot(token=os.getenv("COURIER_BOT"))

customer_dp = Dispatcher()
courier_dp = Dispatcher()


__all__ = [
    "customer_bot",
    "couriers_bot",
    "customer_dp",
    "courier_dp",
]
