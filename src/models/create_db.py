import asyncio
from src.models import engine, Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


if __name__ == "__main__":
    try:
        asyncio.run(create_tables())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(create_tables())

__all__ = ["create_tables"]
