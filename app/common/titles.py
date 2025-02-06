import os
from aiogram.types import FSInputFile


async def get_image_title_user(command: str):
    title_images_user = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "title_images_user"
    )

    image_paths = {
        "/start": "user_start.jpg",
        "/order": "order.jpg",
        "/become_courier": "became_a_courier.jpg",
    }

    image_urls = {
        "/start": "https://ibb.co/x2gqw9M",
        "/order": "https://ibb.co/vQGNt4Q",
        "/become_courier": "https://ibb.co/nCnC75D",
    }

    if command in image_urls:
        return image_urls[command]

    photo_path = os.path.join(title_images_user, image_paths.get(command, ""))
    if os.path.isfile(photo_path):
        return FSInputFile(photo_path)

    return None


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
