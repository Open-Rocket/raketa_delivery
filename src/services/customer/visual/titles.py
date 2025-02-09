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
