import secrets
import string


async def generate_seed():
    """Генерирует уникальный ключ для партнёра"""
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )


__all__ = ["generate_seed"]
