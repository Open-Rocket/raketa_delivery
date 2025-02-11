from dependencies._dependencies import Router

payment_r = Router()
customer_r = Router()
courier_r = Router()
customer_fallback = Router()
courier_fallback = Router()


__all__ = [
    "payment_r",
    "customer_r",
    "courier_r",
    "customer_fallback",
    "courier_fallback",
]
