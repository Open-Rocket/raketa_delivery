import re
import os
from src.config import log
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from textwrap import wrap


class PDFcreator:
    def __init__(self, output_dir: str = "pdf"):
        """Инициализация класса PDFcreator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._register_fonts()

    def _register_fonts(self):
        """Регистрирует пользовательский шрифт DejaVuSans."""
        # Определяем путь к шрифту относительно корня проекта
        base_dir = (
            Path(__file__).resolve().parent.parent
        )  # Переходим на два уровня вверх
        font_path = (
            base_dir / "fonts" / "dejavu-fonts-ttf-2.37" / "ttf" / "DejaVuSans.ttf"
        )

        if not font_path.exists():
            raise FileNotFoundError(f"Файл шрифта не найден: {font_path}")

        pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))

    async def remove_html_tags(self, text: str) -> str:
        """Удаляет HTML-теги из строки."""
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    async def create_earn_requests_pdf(self, data: dict) -> Path:
        """Создает PDF-файл с запросами на вывод средств."""
        output_path = self.output_dir / "earn_requests.pdf"

        pdf = canvas.Canvas(str(output_path), pagesize=letter)
        pdf.setTitle("List of Withdrawal Requests")

        pdf.setFont("Helvetica-Bold", 20)
        x, y = 50, 800

        current_date = datetime.now().strftime("%Y-%m-%d")
        pdf.drawString(x, y - 40, f"Partner Requests - {current_date}")
        y -= 80

        pdf.setFont("Helvetica", 16)
        pdf.drawString(x, y, "No. | Amount rub | TG | Date Y.M.D")
        y -= 30

        pdf.setFont("Helvetica", 12)
        total_sum = 0

        for req_id, (_, user_link, balance, request_date) in data.items():
            line = f"{req_id} | {balance} rub | {user_link} | {request_date}"
            clean_line = await self.remove_html_tags(line)
            pdf.drawString(x, y, clean_line)
            y -= 15
            total_sum += balance

            if y < 50:
                pdf.showPage()
                y = 800

        y -= 30
        pdf.drawString(x, y, f"Total amount to be paid: {total_sum} rub")
        pdf.save()
        return output_path

    async def create_order_data_pdf(self, data: dict) -> Path:
        """Создает PDF-файл с данными о заказе с переносом длинных строк."""
        output_path = self.output_dir / "order_data.pdf"

        pdf = canvas.Canvas(str(output_path), pagesize=letter)
        pdf.setTitle("Order Data")

        pdf.setFont("DejaVuSans", 20)
        x, y = 50, 800

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.drawString(x, y, "Order Information")
        y -= 30

        pdf.setFont("DejaVuSans", 14)
        pdf.drawString(x, y, f"Generated at: {current_date}")
        y -= 40

        pdf.setFont("DejaVuSans", 12)
        max_width = (
            90  # Максимальная длина строки в символах — подбирается опытным путём
        )

        for key, value in data.items():
            formatted_key = key.replace("_", " ").capitalize()
            line = f"{formatted_key}: {value}"

            # Переносим строку, если она слишком длинная
            wrapped_lines = wrap(line, width=max_width)

            for wrapped_line in wrapped_lines:
                pdf.drawString(x, y, wrapped_line)
                y -= 18
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("DejaVuSans", 12)
                    y = 800

        pdf.save()
        return output_path


pdf_creator = PDFcreator()

__all__ = ["pdf_creator"]
