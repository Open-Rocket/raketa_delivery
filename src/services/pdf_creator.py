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
        pdf.drawString(x, y, "SEED | TG_ID | No. | Amount rub | TG | Date Y.M.D")
        y -= 30

        pdf.setFont("Helvetica", 12)
        total_sum = 0

        for req_id, (
            user_seed,
            user_tg_id,
            user_link,
            balance,
            request_date,
        ) in data.items():
            line = f"{user_seed} | {user_tg_id} | {req_id} | {balance} rub | {user_link} | {request_date}"
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
        """Создает PDF-файл с данными о заказе с переносом длинных строк с учётом ширины."""
        output_path = self.output_dir / "order_data.pdf"

        pdf = canvas.Canvas(str(output_path), pagesize=letter)
        pdf.setTitle("Order Data")

        pdf.setFont("DejaVuSans", 20)
        x, y = 50, 800
        right_margin = 550  # правая граница текста (A4 шириной 612 pt)

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.drawString(x, y, "Order Information")
        y -= 30

        pdf.setFont("DejaVuSans", 14)
        pdf.drawString(x, y, f"Generated at: {current_date}")
        y -= 40

        pdf.setFont("DejaVuSans", 12)
        font_name = "DejaVuSans"
        font_size = 12

        for key, value in data.items():
            formatted_key = key.replace("_", " ").capitalize()
            line = f"{formatted_key}: {value}"

            # Правильный перенос строк с учётом ширины
            words = line.split()
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip()
                line_width = pdf.stringWidth(test_line, font_name, font_size)

                if line_width < (right_margin - x):
                    current_line = test_line
                else:
                    pdf.drawString(x, y, current_line)
                    y -= 18
                    current_line = word
                    if y < 50:
                        pdf.showPage()
                        pdf.setFont(font_name, font_size)
                        y = 800

            if current_line:
                pdf.drawString(x, y, current_line)
                y -= 18
                if y < 50:
                    pdf.showPage()
                    pdf.setFont(font_name, font_size)
                    y = 800

        pdf.save()
        return output_path


pdf_creator = PDFcreator()

__all__ = ["pdf_creator"]
