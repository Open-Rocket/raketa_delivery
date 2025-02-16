import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, User, Chat, Update
from aiogram import Bot
from src.config import moscow_time
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from src.app.customer import customer_r


@pytest.mark.asyncio
async def test_router_handling():
    bot = AsyncMock(spec=Bot)
    dp = Dispatcher()
    dp.include_router(customer_r)

    with patch(
        "src.app.customer.cmd_start_customer", new_callable=AsyncMock
    ) as mock_cmd:
        message = Message(
            message_id=1,
            from_user={"id": 56782546, "is_bot": False, "first_name": "Gogich"},
            chat={"id": 1846124, "type": "private"},
            text="/start",
            date=moscow_time,
        )

        update = Update(update_id=123456, message=message)
        await dp.feed_update(bot, update)


# @pytest.mark.asyncio
# async def test_message_sent():
#     user = User(id=56782546, is_bot=False, first_name="Gogich")
#     chat = Chat(id=1846124, type="private")

#     message = AsyncMock(spec=Message)
#     message.answer_photo = AsyncMock()
#     message.from_user = user
#     message.chat = chat
#     message.text = "/start"
#     message.date = moscow_time

#     state = AsyncMock()

#     # rediska = AsyncMock()
#     # rediska.is_reg = AsyncMock(return_value=False)

#     mock_img = AsyncMock()
#     mock_reply_kb = AsyncMock()

#     with patch(
#         "src.utils.title.get_title_customer", AsyncMock(return_value=mock_img)
#     ), patch(
#         "src.utils.kb.get_customer_kb", AsyncMock(return_value=mock_reply_kb)
#     ), patch(
#         "src.app.customer.MessageHandler"
#     ) as MockHandler:

#         mock_handler = MockHandler.return_value
#         mock_handler.delete_previous_message = AsyncMock(return_value=None)
#         mock_handler.handle_new_message = AsyncMock()

#         await cmd_start_customer(message, state)

#         mock_handler.delete_previous_message.assert_called_once_with(chat.id)

#         message.answer_photo.assert_called_with(
#             photo=mock_img,
#             caption=(
#                 "Raketa — современный сервис доставки с минимальными ценами и удобством использования.\n\n"
#                 "Почему выбирают нас?\n\n"
#                 "◉ Низкие цены:\n"
#                 "Наши пешие курьеры находятся рядом с вами, что снижает стоимость и ускоряет доставку.\n\n"
#                 "◉ Простота и удобство:\n"
#                 "С помощью технологий ИИ вы можете быстро оформить заказ и сразу отправить его на выполнение."
#             ),
#             reply_markup=mock_reply_kb,
#             parse_mode="HTML",
#             disable_notification=True,
#         )


# pytest tests/customerBot/test_cmd_start.py -s -v
