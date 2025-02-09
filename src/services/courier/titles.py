import os
from aiogram.types import FSInputFile


async def get_image_title_courier(command: str):
    title_images_courier = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "title_images_courier"
    )

    image_paths = {
        "/start": "courier_start.jpg",
        "/run": "run.jpg",
        "/profile": "courier_profile.jpg",
        "/subs": "subs.jpg",
        "/faq": "courier_faq.jpg",
        "/ai": "courier_ai.jpg",
        "on_way": "courier_on-the-way.jpg",
        "success_payment": "success_payment.jpg",
    }

    if command in image_paths:
        photo_path = os.path.join(title_images_courier, image_paths[command])
        if os.path.isfile(photo_path):
            return FSInputFile(photo_path)

    return None
