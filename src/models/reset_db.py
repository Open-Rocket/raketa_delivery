import asyncio
from src.models import engine, Base


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляет все таблицы
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


if __name__ == "__main__":
    try:
        asyncio.run(reset_db())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(reset_db())

__all__ = ["reset_db"]


# python -m src.models.reset_db
# redis-cli flushdb
