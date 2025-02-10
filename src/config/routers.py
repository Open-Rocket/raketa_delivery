from ._deps import Router

payment = Router()
customer = Router()
courier = Router()


__all__ = ["payment", "customer", "courier"]
