import pytest_asyncio
import redis.asyncio as aioredis
from unittest.mock import AsyncMock


@pytest_asyncio.fixture(scope="function")
async def mock_redis():
    return AsyncMock(aioredis.Redis)
