import os
from datetime import datetime
from typing import Optional, Annotated
from sqlalchemy import ForeignKey, String, BigInteger, Enum, Boolean, DateTime, Text, Float, Date, func, MetaData, text, \
    Table, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, MappedColumn
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import Column, Integer
from dotenv import load_dotenv
import enum
import pytz

from app.database.config_db import settings

load_dotenv()

intPK = Annotated[int, mapped_column(Integer, primary_key=True)]
str_256 = Annotated[str, 256]

sqlalchemy_url = os.getenv("SQLALCHEMY_URL")
engine = create_async_engine(url=settings.DB_URL_asyncpg, echo=False)  # pool_size=5, max_overflow=10
async_session_factory = async_sessionmaker(engine)

moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(tzinfo=None, microsecond=0)
utc_time = datetime.now(pytz.timezone("utc")).replace(tzinfo=None, microsecond=0)


# Enums


class Base(AsyncAttrs, DeclarativeBase):
    # type_annotation_map = {
    #     str_256: String(256)
    #
    # }

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__}{','.join(cols)}>"


class AssociateTables:
    # Ассоциативная таблица для связывания заказов и курьеров
    order_courier_association = Table(
        'order_courier_association', Base.metadata,
        Column('order_id', Integer, ForeignKey('orders.order_id')),
        Column('courier_id', Integer, ForeignKey('users.user_id'))
    )

    # Ассоциативная таблица для связывания заказов и клиентов
    order_customer_association = Table(
        'order_customer_association', Base.metadata,
        Column('order_id', Integer, ForeignKey('orders.order_id')),
        Column('customer_id', Integer, ForeignKey('users.user_id'))
    )


class Role(enum.Enum):
    undefined = "undefined"
    courier = "Курьер"
    customer = "Клиент"


class OrderStatus(enum.Enum):
    PENDING = "Ожидается курьер"
    IN_PROGRESS = "В пути"
    COMPLETED = "Доставлено"
    CANCELLED = "Отменено"


class SubscriptionType(enum.Enum):
    ONE_DAY = 1
    TEN_DAYS = 10
    ONE_MONTH = 30


# Таблицы

class User(Base):
    __tablename__ = "users"

    # Поля
    user_id: Mapped[intPK]  # Основной ID пользователя
    user_tg_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String(100), nullable=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=True)
    user_phone_number: Mapped[str] = mapped_column(String(20), nullable=True)

    # Поля для ролей
    courier_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)  # ID курьера
    customer_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)  # ID клиента

    # Координаты
    user_latitude: Mapped[float] = mapped_column(Float, nullable=True)
    user_longitude: Mapped[float] = mapped_column(Float, nullable=True)

    user_role: Mapped[Role] = mapped_column(Enum(Role), default=Role.undefined)
    user_subscription_status: Mapped[bool] = mapped_column(Boolean, default=False)
    user_registration_date: Mapped[datetime] = mapped_column(DateTime, default=utc_time)

    # Связи с другими таблицами
    user_country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.country_id"), nullable=True)
    user_city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.city_id"), nullable=True)
    user_district_id: Mapped[int] = mapped_column(Integer, ForeignKey("districts.district_id"), nullable=True)

    # Отношения
    user_country = relationship("Country", back_populates="users")
    user_city = relationship("City", back_populates="users")
    user_district = relationship("District", back_populates="users")

    courier_orders = relationship("Order", foreign_keys="Order.courier_id", back_populates="courier")
    customer_orders = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")

    user_statistics = relationship("UserStatistics", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")

    repr_cols_num = 4
    repr_cols = ("user_role",)


class Country(Base):
    __tablename__ = "countries"

    # Поля
    country_id: Mapped[intPK]
    country_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # Отношения с пользователями и городами
    users = relationship("User", back_populates="user_country")
    cities = relationship("City", back_populates="country")
    districts = relationship("District", back_populates="country")


class City(Base):
    __tablename__ = "cities"

    # Поля
    city_id: Mapped[intPK]
    city_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # Связь с Country
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey('countries.country_id'), nullable=True)

    # Отношения с пользователями и районами
    users = relationship("User", back_populates="user_city")
    districts = relationship("District", back_populates="city")
    country = relationship("Country", back_populates="cities")


class District(Base):
    __tablename__ = "districts"

    # Поля
    district_id: Mapped[intPK]
    district_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # Связь с City и Country
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.city_id"), nullable=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey('countries.country_id'), nullable=True)

    # Отношения с пользователями, городами и странами
    users = relationship("User", back_populates="user_district")
    country = relationship("Country", back_populates="districts")
    city = relationship("City", back_populates="districts")


class Order(Base):
    __tablename__ = "orders"

    # Поля
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_description: Mapped[str] = mapped_column(Text, nullable=True)
    order_status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)

    # Внешние ключи для курьера и клиента
    courier_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.courier_id", ondelete="CASCADE"))
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.customer_id", ondelete="CASCADE"))

    # Прочие внешние ключи
    order_country: Mapped[int] = mapped_column(Integer, ForeignKey("countries.country_id"))
    order_city: Mapped[int] = mapped_column(Integer, ForeignKey("cities.city_id"))
    order_district: Mapped[int] = mapped_column(Integer, ForeignKey("districts.district_id"))

    # Отношения с пользователями (курьер и клиент)
    courier = relationship("User", foreign_keys=[courier_id], back_populates="courier_orders")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_orders")

    # Поля времени и адреса
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_time, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_time, onupdate=utc_time, nullable=True)

    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    execution_time: Mapped[float] = mapped_column(Float, nullable=True)

    order_address: Mapped[dict] = mapped_column(JSON, nullable=False)


class UserStatistics(Base):
    __tablename__ = "user_statistics"

    # Поля
    statistics_id: Mapped[intPK]

    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_working_hours: Mapped[float] = mapped_column(Float, default=0.0)  # Общее количество отработанных часов
    total_working_days: Mapped[int] = mapped_column(Integer, default=0)  # Общее количество отработанных дней

    total_earned: Mapped[float] = mapped_column(Float,
                                                default=0.0)  # Сумма всех выполненных заказов со статусом COMPLETED
    average_order_time: Mapped[float] = mapped_column(Float, default=0.0)  # Средняя скорость выполнения заказов
    fastest_order_time: Mapped[float] = mapped_column(Float, nullable=True)  # Самое быстрое время выполнения заказа

    average_earnings_per_day: Mapped[float] = mapped_column(Float, default=0.0)  # Средний заработок в день
    average_earnings_per_hour: Mapped[float] = mapped_column(Float, default=0.0)  # Средний заработок в час

    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))

    user = relationship("User", back_populates="user_statistics")


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[intPK]

    # Поле для типа подписки
    subscription_type: Mapped[SubscriptionType] = mapped_column(Enum(SubscriptionType), nullable=False)

    start_date: Mapped[datetime] = mapped_column(DateTime, default=moscow_time, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Стоимость подписки
    subscription_cost: Mapped[float] = mapped_column(Float, nullable=False)

    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)

    user = relationship("User", back_populates="subscriptions")


class DailyEvent(Base):
    __tablename__ = "daily_events"

    # Основные поля
    daily_event_id: Mapped[intPK]
    event_date: Mapped[Date] = mapped_column(Date, primary_key=True, default=func.current_date(), nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    canceled_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_subscriptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_order_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fastest_order_time: Mapped[float] = mapped_column(Float, nullable=True)  # В секундах или минутах
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    support_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Поле для дополнительных комментариев или данных
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return (f"DailyEvent(date={self.event_date}, total_orders={self.total_orders}, "
                f"completed_orders={self.completed_orders}, total_revenue={self.total_order_revenue})")


# Функция
async def async_main():
    async with engine.begin() as conn:
        # engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
