import fitz
import string
import secrets
from io import BytesIO
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from src.utils.titles import title
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont


class SeedMaker:

    @staticmethod
    async def generate_seed():
        """Генерирует уникальный ключ для партнёра"""
        return "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )

    @staticmethod
    async def get_business_card(
        seed_key: str,
        type_template: str,
    ) -> bytes:
        """Генерирует визитку с уникальным ключом"""

        template = await title.get_adv_partner(type_template)

        if not template:
            raise ValueError("Ошибка: шаблон PDF не найден или пуст.")

        try:
            doc = fitz.open(stream=template, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Не удалось открыть PDF-шаблон: {str(e)}")

        page = doc[0]

        page_width = page.rect.width
        page_height = page.rect.height

        buffer = BytesIO()

        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        font_size = (
            44
            if type_template in ("business_card_courier", "business_card_customer")
            else 150
        )

        c.setFont("Helvetica-Bold", font_size)

        c.setFillColorRGB(1, 1, 1)

        x, y = (
            (205, 85)
            if type_template in ("business_card_courier", "business_card_customer")
            else (470, 170)
        )
        c.drawString(x, y, seed_key)

        c.showPage()
        c.save()

        buffer.seek(0)

        generated_pdf = buffer.getvalue()

        generated_doc = fitz.open(stream=generated_pdf, filetype="pdf")

        doc = fitz.open(stream=template, filetype="pdf")
        original_page = doc[0]

        original_page.show_pdf_page(original_page.rect, generated_doc, 0)

        final_buffer = BytesIO()
        doc.save(final_buffer)
        doc.close()

        return final_buffer.getvalue()

    @staticmethod
    async def get_qr_codes(
        type_of_user: str,
    ) -> tuple:
        """Возвращает QR-коды для пользователя"""

        if "courier" in type_of_user:
            return await title.get_adv_partner(
                "QR_courier_white"
            ), await title.get_adv_partner("QR_courier_black")
        else:
            return await title.get_adv_partner(
                "QR_customer_white"
            ), await title.get_adv_partner("QR_customer_black")

    @staticmethod
    async def get_logo() -> tuple:
        """Возвращает логотип"""

        font_logo_white = await title.get_adv_partner("font_logo_white")
        font_logo_black = await title.get_adv_partner("font_logo_black")
        logo_white = await title.get_adv_partner("logo_white")
        logo_black = await title.get_adv_partner("logo_black")

        return font_logo_white, font_logo_black, logo_white, logo_black

    @staticmethod
    async def get_seed_key_svg(seed_key: str) -> tuple:
        """Создаёт два SVG с SEED-ключом: один с белым текстом, второй с чёрным"""

        width, height = 1200, 300
        font_size = 160

        # Создание SVG с белым текстом (жирным)
        svg_white = f"""<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}">
            <text x="50%" y="75%" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" fill="white" font-weight="bold">{seed_key}</text>
        </svg>"""

        # Создание SVG с чёрным текстом (жирным)
        svg_black = f"""<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}">
            <text x="50%" y="75%" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" fill="black" font-weight="bold">{seed_key}</text>
        </svg>"""

        return svg_white, svg_black


seed_maker = SeedMaker()

__all__ = [
    "seed_maker",
]
