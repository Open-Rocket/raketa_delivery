from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session_factory, moscow_time, Order
from app.database.models import User, Courier
from sqlalchemy import select, update, delete, desc
import json


class UserData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def set_user(self, tg_id: int):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if not user:
                new_user = User(user_tg_id=tg_id)
                session.add(new_user)
                await session.commit()

    async def set_username(self, tg_id: int, name: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_name = name
                await session.commit()

    async def set_user_email(self, tg_id: int, email: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_email = email
                await session.commit()

    async def set_user_phone(self, tg_id: int, phone: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_phone_number = phone
                await session.commit()

    async def get_user_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                return (user.user_name or "...", user.user_email or "...", user.user_phone_number or "...")
            return ("...", "...", "...")


class CourierData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def set_courier(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if not courier:
                new_courier = Courier(courier_tg_id=tg_id)
                session.add(new_courier)
                await session.commit()

    async def set_courier_name(self, tg_id: int, name: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_name = name
                await session.commit()

    async def set_courier_email(self, tg_id: int, email: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_email = email
                await session.commit()

    async def set_courier_phone(self, tg_id: int, phone: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_phone_number = phone
                await session.commit()

    async def get_courier_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                return (
                courier.courier_name or "...", courier.courier_email or "...", courier.courier_phone_number or "...")
            return ("...", "...", "...")


# async def get_users():
#     async with async_session_factory() as session:  # Используйте свой async_session
#         result = await session.execute(select(User))
#         users = result.scalars().all()  # Получение всех пользователей
#         print(users)


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


user_data = UserData(async_session_factory)
courier_data = CourierData(async_session_factory)
