from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session_factory, moscow_time, Order
from app.database.models import User
from sqlalchemy import select, update, delete, desc
import json


async def set_user(tg_id):
    async with async_session_factory() as session:
        user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

        if not user:
            session.add(User(user_tg_id=tg_id))
            await session.commit()


async def set_username(tg_id: int, name: str):
    async with async_session_factory() as session:
        user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

        if user:
            user.user_name = name
            await session.commit()


async def set_user_email(tg_id: int, email: str):
    async with async_session_factory() as session:
        user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

        if user:
            user.user_email = email
            await session.commit()


async def set_user_phone(tg_id: int, phone: str):
    async with async_session_factory() as session:
        user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

        if user:
            user.user_phone_number = phone
            await session.commit()


async def get_user_info(tg_id: int):
    async with async_session_factory() as session:
        user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

        if user:
            if user.user_name and user.user_email and user.user_phone_number:
                return user.user_name, user.user_email, user.user_phone_number
            else:
                return "...", "...", "..."


async def get_users():
    async with async_session_factory() as session:  # Используйте свой async_session
        result = await session.execute(select(User))
        users = result.scalars().all()  # Получение всех пользователей
        print(users)


async def complete_order(order_id: int, session: AsyncSession):
    # Получаем заказ из базы данных
    order = await session.get(Order, order_id)

    # Устанавливаем время завершения заказа
    order.completed_at = moscow_time()

    # Рассчитываем время выполнения (разница в минутах)
    if order.created_at and order.completed_at:
        order.execution_time = (order.completed_at - order.created_at).total_seconds() // 60

    # Обновляем запись в базе данных
    await session.commit()
