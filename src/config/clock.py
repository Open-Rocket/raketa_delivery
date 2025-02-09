from .__deps__ import pytz, datetime


moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(
    tzinfo=None, microsecond=0
)
utc_time = datetime.now(pytz.timezone("utc")).replace(tzinfo=None, microsecond=0)


__all__ = ["moscow_time", "utc_time"]
