import re
from datetime import datetime
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from src.config import log


class PDFcreator:
    def __init__(self, output_dir: str = "pdf"):
        """Инициализация класса PDFcreator."""
        self.output_dir = Path(output_dir)

    async def remove_html_tags(self, text: str) -> str:
        """Чистит текст от HTML-тегов."""
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    async def create_earn_requests_pdf(self, data: dict) -> Path:
        """Создает PDF-файл с запросами на вывод средств."""

        filename = f"earn_requests.pdf"
        output_path = self.output_dir / filename

        pdf = canvas.Canvas(str(output_path), pagesize=letter)
        pdf.setTitle("List of Withdrawal Requests")

        # Настройка шрифта для заголовка (жирный и размер 20)
        pdf.setFont("Helvetica-Bold", 20)

        x, y = 50, 800

        # Заголовок
        current_date = datetime.now().strftime("%Y-%m-%d")
        title_offset = 50
        pdf.drawString(x, y - title_offset, f"Partner Requests - {current_date}")
        y -= title_offset + 20

        # Настройка шрифта для остальных строк (обычный и размер 16)
        pdf.setFont("Helvetica", 16)

        # Заголовок таблицы
        header_offset = 50
        pdf.drawString(x, y - header_offset, "No. | Amount rub | TG | Date Y.M.D")
        y -= header_offset + 30

        total_sum = 0

        # Основное содержимое
        for req_id, (_, user_link, balance, request_date) in data.items():
            line = f"{req_id} | {balance} rub | {user_link} | {request_date}"
            clean_line = await self.remove_html_tags(line)
            pdf.drawString(x, y, clean_line)
            y -= 15
            total_sum += balance

            # Переход на новую страницу, если достигнут низ страницы
            if y < 50:
                pdf.showPage()
                y = 800

        # Итоговая сумма
        total_offset = 30
        pdf.drawString(x, y - total_offset, f"Total amount to be paid: {total_sum} rub")

        pdf.save()
        return output_path


pdf_creator = PDFcreator()

__all__ = ["pdf_creator"]
