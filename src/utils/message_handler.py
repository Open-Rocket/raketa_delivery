from aiogram.fsm.context import FSMContext


class MessageHandler:
    def __init__(self, state: FSMContext, bot):
        self.state = state
        self.bot = bot

    async def delete_previous_message(self, chat_id):
        data = await self.state.get_data()
        previous_message_id = data.get("previous_message_id")
        if previous_message_id:
            try:
                await self.bot.delete_message(
                    chat_id=chat_id, message_id=previous_message_id
                )
            except Exception as e:
                print(f"Failed to delete the previous message: {e}")

    async def handle_new_message(self, new_message, current_message):
        await self.state.update_data(previous_message_id=new_message.message_id)
        await current_message.delete()

    async def delete_previous_messages(self, message=None, chat_id=None):
        data = await self.state.get_data()
        previous_message_ids = data.get("previous_message_ids", [])

        for message_id in previous_message_ids:
            try:
                await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"Failed to delete the previous message: {e}")

    async def update_previous_message_ids(self, new_message_ids: list):
        await self.state.update_data(previous_message_ids=new_message_ids)


__all__ = ["MessageHandler"]
