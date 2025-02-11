from _dependencies import Router

payment = Router()
customer_r = Router()
courier_r = Router()
customer_fallback = Router()
courier_fallback = Router()


__all__ = [
    "payment",
    "customer_r",
    "courier_r",
    "customer_fallback",
    "courier_fallback",
]
