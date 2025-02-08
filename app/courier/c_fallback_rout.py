from aiogram import Router
from aiogram.types import Message

c_fallback_router = Router()


@c_fallback_router.message()
async def handle_unrecognized_message(message: Message):
    await message.delete()
