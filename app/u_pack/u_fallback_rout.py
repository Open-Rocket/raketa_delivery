from aiogram import Router
from aiogram.types import Message

fallback_router = Router()


@fallback_router.message()
async def handle_unrecognized_message(message: Message):
    await message.delete()
