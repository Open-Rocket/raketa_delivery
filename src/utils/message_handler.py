from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.config import log
from src.confredis import rediska


class MessageHandler:

    async def catch(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        new_message: Message,
        current_message: Message,
        delete_previous: bool = True,
    ):
        """Отлавливает новое сообщение"""

        if delete_previous:
            await self._delete_previous_message(bot, user_id, chat_id)

        await rediska.set_message(bot.id, user_id, new_message)
        if current_message:
            await current_message.delete()

    async def _delete_previous_message(
        self,
        bot: Bot,
        user_id: int,
        chat_id: int,
    ):
        """Удаляет предыдущее сообщение"""
        previous_message_id = await rediska.get_message_id(bot.id, user_id)
        if previous_message_id:
            try:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=previous_message_id,
                )
                await rediska.delete_message(bot.id, user_id)
            except Exception as e:
                log.error(f"Failed to delete the previous message: {e}")


handler = MessageHandler()


__all__ = [
    "MessageHandler",
    "MessageHandler_2",
    "handler",
]
