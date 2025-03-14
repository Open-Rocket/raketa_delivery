import os
import enum
from datetime import datetime
from typing import Optional, Annotated
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import LargeBinary


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
from src.config import Time, db_settings


load_dotenv()

sqlalchemy_url = os.getenv("SQLALCHEMY_URL")
engine = create_async_engine(url=db_settings.DB_URL_asyncpg, echo=False)
async_session_factory = async_sessionmaker(engine)

intPK = Annotated[int, mapped_column(Integer, primary_key=True)]
textData = Annotated[str, mapped_column(Text, nullable=True)]
stringData = Annotated[str, mapped_column(String(256), nullable=True)]
intData = Annotated[int, mapped_column(Integer, nullable=True)]
intDataUnique = Annotated[int, mapped_column(Integer, unique=True, nullable=True)]
floatData = Annotated[float, mapped_column(Float, nullable=True)]
coordinates = Annotated[tuple, mapped_column(ARRAY(String), nullable=True)]
str_256 = Annotated[str, 256]
datetimeData = Annotated[datetime, mapped_column(DateTime)]
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
    agent = "Агент"


class OrderStatus(enum.Enum):
    PENDING = "Ожидается курьер"
    IN_PROGRESS = "В пути"
    COMPLETED = "Доставлен"
    CANCELLED = "Отменен"


# Tables


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[intPK]

    customer_tg_id: Mapped[intDataUnique]
    customer_name: Mapped[stringData]
    customer_phone: Mapped[stringData]
    customer_city: Mapped[stringData]
    customer_accept_terms_of_use: Mapped[stringData]
    customer_registration_date: Mapped[datetimeData]

    orders = relationship("Order", back_populates="customers")


class Courier(Base):
    __tablename__ = "couriers"

    courier_id: Mapped[intPK]

    courier_tg_id: Mapped[intDataUnique]
    courier_name: Mapped[stringData]
    courier_phone: Mapped[stringData]
    courier_city: Mapped[stringData]
    courier_accept_terms_of_use: Mapped[stringData]
    courier_registration_date: Mapped[datetimeData]

    orders_active_now: Mapped[intData]

    orders = relationship("Order", back_populates="couriers")
    subscription = relationship("Subscription", back_populates="couriers")


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[intPK]

    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=True
    )
    courier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("couriers.courier_id", ondelete="CASCADE"), nullable=True
    )

    created_at_moscow_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    started_at_moscow_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at_moscow_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    order_city: Mapped[stringData]

    customer_name: Mapped[stringData]
    customer_phone: Mapped[stringData]
    customer_tg_id: Mapped[intData]

    courier_tg_id: Mapped[intData]
    courier_name: Mapped[stringData]
    courier_phone: Mapped[stringData]

    delivery_object: Mapped[stringData]
    distance_km: Mapped[floatData]
    price_rub: Mapped[intData]
    description: Mapped[textData]
    full_rout: Mapped[stringData]

    starting_point: Mapped[coordinates]

    order_forma: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    couriers = relationship("Courier", back_populates="orders")
    customers = relationship("Customer", back_populates="orders")


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[intPK]

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
    "engine",
    "Base",
]
