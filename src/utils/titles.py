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
        """Возвращает картинку для партнера"""

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

    import os

    @staticmethod
    async def get_adv_partner(command: str) -> bytes | None:
        """Возвращает рекламные данные для партнера как bytes"""

        dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../..", "public"
        )

        paths = {
            "business_card_courier": "business_card_courier.pdf",
            "business_card_customer": "business_card_customer.pdf",
            "buklet_customer": "buklet_customer.pdf",
            "buklet_courier": "buklet_courier.pdf",
            "QR_courier_white": "QR_courier_white.png",
            "QR_courier_black": "QR_courier_black.png",
            "QR_customer_white": "QR_customer_white.png",
            "QR_customer_black": "QR_customer_black.png",
            "font_logo_white": "font_logo_white.png",
            "font_logo_black": "font_logo_black.png",
            "logo_white": "logo_white.png",
            "logo_black": "logo_black.png",
        }

        path = os.path.join(dir, paths.get(command, ""))

        if os.path.isfile(path):
            # Открываем файл в бинарном режиме и конвертируем его в bytes
            with open(path, "rb") as f:
                pdf_bytes = f.read()
            return pdf_bytes

        return None


title = Title()

__all__ = ["title"]
