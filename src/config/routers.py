from aiogram import Router


customer_r = Router()
courier_r = Router()

customer_fallback = Router()
courier_fallback = Router()
payment_r = Router()

admin_r = Router()
admin_fallback = Router()

partner_r = Router()
partner_fallback = Router()


__all__ = [
    "payment_r",
    "customer_r",
    "courier_r",
    "customer_fallback",
    "courier_fallback",
    "admin_r",
    "admin_fallback",
    "partner_r",
    "partner_fallback",
]
