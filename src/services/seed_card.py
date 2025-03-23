import io
import fitz
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from aiogram.types import BufferedInputFile
from PIL import Image, ImageDraw, ImageFont


# Размер стандартной визитки: 85x55 мм
CARD_WIDTH, CARD_HEIGHT = 85 * mm, 55 * mm


async def generate_partner_card(seed_key: str) -> bytes:
    """
    Генерирует PDF с визиткой партнера, содержащей его уникальный ключ.
    """
    # Создание PDF-буфера
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=(CARD_WIDTH, CARD_HEIGHT))

    # Настройки текста
    text_x, text_y = 10 * mm, 40 * mm  # Координаты на визитке
    pdf.setFont("Helvetica", 12)
    pdf.drawString(text_x, text_y, "Ваш партнерский ключ:")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(1, 0, 0)  # Красный цвет
    pdf.drawString(text_x, text_y - 10, seed_key)

    pdf.showPage()
    pdf.save()

    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


async def add_seed_key_to_pdf(seed_key: str, template_path: str) -> bytes:
    """Добавляет seed_key в готовый PDF и возвращает его в виде bytes."""

    # Открываем шаблон PDF
    doc = fitz.open(template_path)
    page = doc[
        0
    ]  # Берём первую страницу (если нужно изменить несколько, допиши логику)

    # Настройки текста (шрифт, размер, координаты)
    text_position = (100, 200)  # Укажи нужные координаты (x, y)
    font_size = 12

    # Добавляем текст
    page.insert_text(text_position, seed_key, fontsize=font_size, color=(0, 0, 0))

    # Сохраняем в байты
    pdf_bytes = doc.write()
    doc.close()

    return pdf_bytes
