import os
from aiogram.types import Message, FSInputFile


async def get_image_title_user(command: str):
    title_images_user = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "title_images_user"
    )

    image_paths = {
        "/start": os.path.join(title_images_user, "user_start.jpg"),
        "/order": os.path.join(title_images_user, "order.jpg"),
        "/become_courier": os.path.join(title_images_user, "became_a_courier.jpg"),
    }

    image_urls = {
        "/start": "https://ibb.co/x2gqw9M",
        "/order": "https://ibb.co/vQGNt4Q",
        "/become_courier": "https://ibb.co/nCnC75D",
        # "/subs": "https://ltdfoto.ru/images/2024/08/31/subs.jpg",
    }

    if command in image_urls:
        photo = image_urls[command]
        return photo

    elif command in image_paths and os.path.isfile(image_paths[command]):
        photo_path = image_paths[command]
        try:
            # Пробуем создать FSInputFile
            photo = FSInputFile(photo_path)
            return photo
        except Exception as e:
            # Ловим и выводим ошибки, если они возникают
            print(f"Ошибка при создании FSInputFile: {e}")
            return None
    else:
        # Если файл не найден, возвращаем None
        print(f"Файл не найден по пути: {image_paths.get(command)}")
        return None


async def get_image_title_courier(command: str):
    title_images_courier = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "title_images_courier"
    )

    image_paths = {
        "/start": os.path.join(title_images_courier, "courier_start.jpg"),
        "/run": os.path.join(title_images_courier, "run.jpg"),
        "/profile": os.path.join(title_images_courier, "courier_profile.jpg"),
        "/subs": os.path.join(title_images_courier, "subs.jpg"),
        "/faq": os.path.join(title_images_courier, "courier_faq.jpg"),
        "/ai": os.path.join(title_images_courier, "courier_ai.jpg"),
        "on_way": os.path.join(title_images_courier, "courier_on-the-way.jpg"),
        "success_payment": os.path.join(title_images_courier, "success_payment.jpg"),
    }

    # image_urls = {
    #     "/order": "https://ltdfoto.ru/images/2024/08/31/order.jpg>",
    #     "/run": "https://ltdfoto.ru/images/2024/08/31/run.jpg",
    #     "/profile": "https://ltdfoto.ru/images/2024/08/31/set_profile.jpg",
    #     "/subs": "https://ltdfoto.ru/images/2024/08/31/subs.jpg",
    #     "/faq": "https://ltdfoto.ru/images/2024/08/31/faq.jpg",
    #     "/ai": "https://ltdfoto.ru/images/2024/08/31/ai.jpg",
    #     "/admin": "https://ltdfoto.ru/images/2024/08/31/admin.jpg",
    #     "begin": "https://ltdfoto.ru/images/2024/08/31/start.jpg",
    #     "p.profile": "https://ltdfoto.ru/images/2024/08/31/pprofile.jpg",
    #     "с.profile": "https://ltdfoto.ru/images/2024/08/31/dprofile.jpg",
    #     "on_way": "https://ltdfoto.ru/images/2024/08/31/on_the_way.jpg"
    # }

    # Проверяем, существует ли файл по пути
    if command in image_paths and os.path.isfile(image_paths[command]):
        photo_path = image_paths[command]
        try:
            # Пробуем создать FSInputFile
            photo = FSInputFile(photo_path)
            return photo
        except Exception as e:
            # Ловим и выводим ошибки, если они возникают
            print(f"Ошибка при создании FSInputFile: {e}")
            return None
    else:
        # Если файл не найден, возвращаем None
        print(f"Файл не найден по пути: {image_paths.get(command)}")
        return None
