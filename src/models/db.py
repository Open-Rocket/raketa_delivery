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


class GlobalSettings(Base):
    __tablename__ = "global_settings"

    global_settings_id: Mapped[intPK]

    service_is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    free_period_days: Mapped[intData] = mapped_column(Integer, default=10)
    order_price_per_km: Mapped[intData] = mapped_column(Integer, default=38)
    order_max_price: Mapped[intData] = mapped_column(Integer, default=100)
    subs_price: Mapped[intData] = mapped_column(Integer, default=99000)
    discount_percent_courier: Mapped[intData] = mapped_column(Integer, default=15)
    discount_percent_first_order: Mapped[intData] = mapped_column(Integer, default=15)


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[intPK]

    partner_id = mapped_column(
        Integer,
        ForeignKey("partners.partner_id", ondelete="CASCADE"),
        nullable=True,
    )

    seed_key_id = mapped_column(
        Integer,
        ForeignKey("seed_keys.seed_key_id"),
        nullable=True,
    )

    customer_tg_id: Mapped[intDataUnique]
    customer_name: Mapped[stringData]
    customer_phone: Mapped[stringData]
    customer_city: Mapped[stringData]
    customer_accept_terms_of_use: Mapped[stringData]
    customer_registration_date: Mapped[datetimeData]

    orders = relationship("Order", back_populates="customer")
    seed_key = relationship("SeedKey", back_populates="customers")
    partner = relationship("Partner", back_populates="customers")


class Courier(Base):
    __tablename__ = "couriers"

    courier_id: Mapped[intPK]

    partner_id = mapped_column(
        Integer,
        ForeignKey("partners.partner_id", ondelete="CASCADE"),
        nullable=True,
    )

    seed_key_id = mapped_column(
        Integer,
        ForeignKey("seed_keys.seed_key_id"),
        nullable=True,
    )

    courier_tg_id: Mapped[intDataUnique]
    courier_name: Mapped[stringData]
    courier_phone: Mapped[stringData]
    courier_city: Mapped[stringData]
    courier_accept_terms_of_use: Mapped[stringData]
    courier_registration_date: Mapped[datetimeData]

    orders_active_now: Mapped[intData]

    orders = relationship("Order", back_populates="courier")
    subscription = relationship("Subscription", back_populates="couriers")
    partner = relationship("Partner", back_populates="couriers")
    seed_key = relationship("SeedKey", back_populates="couriers")


class Partner(Base):
    __tablename__ = "partners"

    partner_id: Mapped[intPK]

    partner_tg_id: Mapped[intDataUnique]
    partner_name: Mapped[stringData]
    partner_phone: Mapped[stringData]
    partner_city: Mapped[stringData]
    partner_registration_date: Mapped[datetimeData]

    seed_key = relationship("SeedKey", uselist=False, back_populates="partner")

    couriers = relationship("Courier", back_populates="partner")
    customers = relationship("Customer", back_populates="partner")


class SeedKey(Base):
    __tablename__ = "seed_keys"

    seed_key_id: Mapped[intPK]
    partner_id = mapped_column(
        Integer,
        ForeignKey("partners.partner_id", ondelete="CASCADE"),
        unique=True,
    )
    seed_key: Mapped[stringData] = mapped_column(String, unique=True)

    partner = relationship("Partner", back_populates="seed_key")
    couriers = relationship("Courier", back_populates="seed_key")
    customers = relationship("Customer", back_populates="seed_key")


class Admin(Base):
    __tablename__ = "admins"

    admin_id: Mapped[intPK]

    admin_tg_id: Mapped[intDataUnique]
    admin_name: Mapped[stringData]
    admin_phone: Mapped[stringData]


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[intPK]

    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=True,
    )
    courier_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("couriers.courier_id", ondelete="CASCADE"),
        nullable=True,
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

    courier = relationship("Courier", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[intPK]

    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    courier_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("couriers.courier_id"),
        nullable=False,
    )

    couriers = relationship("Courier", back_populates="subscription")


__all__ = [
    "async_session_factory",
    "Customer",
    "Courier",
    "Admin",
    "Partner",
    "SeedKey",
    "Order",
    "OrderStatus",
    "Subscription",
    "GlobalSettings" "engine",
    "Base",
]
