import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.common.message_handler import MessageHandler

admin_router = Router()


@admin_router.message(F.text == "/admin")
async def cmd_admin(message: Message, state: FSMContext):
    # handler = MessageHandler(state, message.bot)
    # await handler.delete_previous_message(message.chat.id)
    # photo_title = await get_image_title_user(message.text)
    # reply_kb = await get_user_kb(message)
    # await asyncio.sleep(0)
    #
    # new_message = await get_message(message=message, photo_title=photo_title, reply_kb=reply_kb)
    # await handler.handle_new_message(new_message, message)
    pass
