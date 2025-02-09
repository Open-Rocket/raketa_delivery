import pytz
from datetime import datetime
from ai.ai_assistant import AssistantAi


moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(
    tzinfo=None, microsecond=0
)
