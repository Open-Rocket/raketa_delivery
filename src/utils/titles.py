import os
from aiogram.types import FSInputFile


class Title:

    @staticmethod
    async def get_title_courier(command: str) -> FSInputFile | None:
        """Возвращает картинку для курьера"""

        dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../..", "public"
        )

        paths = {
            "/start": "courier_start.jpg",
            "/run": "run.jpg",
            "/profile": "courier_profile.jpg",
            "/subs": "subs.jpg",
            "/faq": "courier_faq.jpg",
            "/ai": "courier_ai.jpg",
            "/become_partner": "partners.jpg",
            "on_way": "courier_on-the-way.jpg",
            "success_payment": "success_payment.jpg",
            "first_run": "run_first.jpg",
        }

        img = os.path.join(dir, paths.get(command, ""))
        if os.path.isfile(img):
            return FSInputFile(img)

        return None

    @staticmethod
    async def get_title_customer(command: str) -> FSInputFile | None:
        """Возвращает картинку для клиента"""

        dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../..", "public"
        )

        paths = {
            "/start": "customer_start.jpg",
            "/order": "order.jpg",
            "/become_courier": "became_a_courier.jpg",
            "/become_partner": "partners.jpg",
        }

        img = os.path.join(dir, paths.get(command, ""))
        if os.path.isfile(img):
            return FSInputFile(img)

        return None

    @staticmethod
    async def get_title_partner(command: str) -> FSInputFile | None:
        """Возвращает картинку для клиента"""

        dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../..", "public"
        )

        paths = {
            "/start": "partner_start.jpg",
        }

        img = os.path.join(dir, paths.get(command, ""))
        if os.path.isfile(img):
            return FSInputFile(img)

        return None


title = Title()

__all__ = ["title"]
