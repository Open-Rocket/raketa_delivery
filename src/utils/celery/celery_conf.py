from celery import Celery
from datetime import timedelta


app_celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["src.utils.tasks"],
)


app_celery.conf.update(
    task_pool="gevent",
    result_expires=None,
    task_track_started=True,
    beat_schedule={
        "send_notification_every_hour": {
            "task": "src.utils.tasks.send_notification_to_couriers",
            "schedule": timedelta(seconds=5),
        },
    },
)


"""

celery -A src.utils.celery.celery_conf.app_celery worker --loglevel=info
celery -A src.utils.celery.celery_conf.app_celery beat --loglevel=info

"""
