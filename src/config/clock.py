import pytz
from datetime import datetime


class Time:

    @staticmethod
    async def get_moscow_time():
        moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(
            tzinfo=None, microsecond=0
        )
        return moscow_time

    @staticmethod
    async def get_utc_time():
        utc_time = datetime.now(pytz.timezone("utc")).replace(
            tzinfo=None, microsecond=0
        )
        return utc_time


__all__ = ["Time"]
