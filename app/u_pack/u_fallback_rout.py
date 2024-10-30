from aiogram import Router
from aiogram.types import Message

u_fallback_router = Router()


# @u_fallback_router.message()
# async def handle_unrecognized_message(message: Message):
#     msg = message.text
#     print(msg)
#     await message.delete()
