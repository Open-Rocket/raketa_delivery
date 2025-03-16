from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.config import log
from src.confredis import rediska


class MessageHandler:
    def __init__(self, state: FSMContext, bot: Bot):
        self.state = state
        self.bot = bot

    async def handle_new_message(self, new_message, current_message):
        """Отлавливает новое сообщение"""

        await self.state.update_data(previous_message_id=new_message.message_id)
        await current_message.delete()

    async def delete_previous_message(self, chat_id):
        """Удаляет предыдущее сообщение"""

        data = await self.state.get_data()
        previous_message_id = data.get("previous_message_id")
        if previous_message_id:
            try:
                await self.bot.delete_message(
                    chat_id=chat_id, message_id=previous_message_id
                )

            except Exception as e:
                log.error(f"Failed to delete the previous message: {e}")

    async def update_previous_message_ids(self, new_message_ids: list):
        await self.state.update_data(previous_message_ids=new_message_ids)


class MessageHandler2:

    async def catch(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        new_message: Message | None,
        current_message: Message,
        delete_previous: bool = True,
    ):
        """Отлавливает новое сообщение"""

        if delete_previous:
            await self._delete_previous_message(bot, user_id, chat_id)

        if new_message:
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
                log.error(f"Ошибка удаления предыдущего сообщения: {e}")


handler = MessageHandler2()


__all__ = [
    "handler",
]
