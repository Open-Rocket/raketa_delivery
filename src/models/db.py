import os
import enum
from datetime import datetime
from typing import Optional, Annotated
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column,
    relationship,
)

from sqlalchemy import (
    ForeignKey,
    String,
    BigInteger,
    Enum,
    Boolean,
    DateTime,
    Text,
    Float,
    Integer,
)
from config import db_settings, moscow_time, utc_time


load_dotenv()

sqlalchemy_url = os.getenv("SQLALCHEMY_URL")
engine = create_async_engine(url=db_settings.DB_URL_asyncpg, echo=False)
async_session_factory = async_sessionmaker(engine)

intPK = Annotated[int, mapped_column(Integer, primary_key=True)]
textData = Annotated[str, mapped_column(Text, nullable=True)]
stringData = Annotated[str, mapped_column(String(256), nullable=True)]
intData = Annotated[int, mapped_column(Integer, nullable=True)]
floatData = Annotated[float, mapped_column(Float, nullable=True)]
coordinates = Annotated[tuple, mapped_column(ARRAY(String), nullable=True)]
str_256 = Annotated[str, 256]
datetimeData = Annotated[datetime, mapped_column(DateTime, default=utc_time)]
full_address_data = Annotated[list, mapped_column(JSONB, nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__}{','.join(cols)}>"


class Role(enum.Enum):
    undefined = "undefined"
    courier = "Курьер"
    customer = "Клиент"


class OrderStatus(enum.Enum):
    PENDING = "Ожидается курьер"
    IN_PROGRESS = "В пути"
    COMPLETED = "Доставлен"
    CANCELLED = "Отменен"


# Tables


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[intPK]

    customer_tg_id: Mapped[intData]
    customer_name: Mapped[stringData]
    customer_phone: Mapped[stringData]
    customer_city: Mapped[stringData]
    customer_accept_terms_of_use: Mapped[stringData]
    customer_registration_date: Mapped[datetimeData]

    orders = relationship("Order", back_populates="user")


class Courier(Base):
    __tablename__ = "couriers"

    courier_id: Mapped[intPK]

    courier_tg_id: Mapped[int] = mapped_column(BigInteger)
    courier_name: Mapped[str] = mapped_column(String(100), nullable=True)
    courier_phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    courier_default_city: Mapped[stringData]
    courier_accept_terms_of_use: Mapped[stringData]
    courier_registration_date: Mapped[stringData]

    orders = relationship("Order", back_populates="courier")
    subscription = relationship("Subscription", back_populates="couriers")


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[intPK]

    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True
    )
    courier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("couriers.courier_id", ondelete="CASCADE"), nullable=True
    )

    created_at_moscow_time: Mapped[datetime] = mapped_column(
        DateTime, default=moscow_time, nullable=True
    )
    order_city: Mapped[stringData]
    customer_name: Mapped[stringData]
    customer_phone: Mapped[stringData]
    order_addresses_data: Mapped[full_address_data]
    delivery_object: Mapped[stringData]
    distance_km: Mapped[floatData]
    price_rub: Mapped[intData]
    description: Mapped[textData]
    full_rout: Mapped[stringData]

    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False), nullable=False
    )

    courier = relationship("Courier", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[intPK]

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subscription_cost: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime] = mapped_column(
        DateTime, default=moscow_time, nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    courier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("couriers.courier_id"), nullable=False
    )

    couriers = relationship("Courier", back_populates="subscription")


__all__ = [
    "async_session_factory",
    "Customer",
    "Courier",
    "Order",
    "OrderStatus",
    "Subscription",
    "drop_create_db",
]


# Функция
async def drop_create_db():
    async with engine.begin() as conn:
        # engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
