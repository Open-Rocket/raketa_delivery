import pytest
from unittest.mock import AsyncMock
from confredis import RedisService


@pytest.mark.asyncio
async def test_set_user_info(mock_redis):
    """Проверяем, что set_user_info сохраняет данные в Redis"""

    redis = RedisService(mock_redis)
    mock_redis.hset = AsyncMock(return_value=True)
    result = await redis.set_user_info(1234, "Ruslan", "89993501515")

    assert result is True


@pytest.mark.asyncio
async def test_get_user_info(mock_redis):
    """Проверяем, что get_user_info возвращает корректные данные"""

    mock_redis.hgetall = AsyncMock(
        return_value={b"name": b"Ruslan", b"phone": b"89993501515"}
    )

    redis = RedisService(mock_redis)

    name, phone = await redis.get_user_info(1)

    assert name == "Ruslan"
    assert phone == "89993501515"
