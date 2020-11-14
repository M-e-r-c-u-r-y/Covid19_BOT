from celery import Celery
from celery.schedules import crontab
import os

DEFAULT = "10"
POLLING_MINUTES = os.environ.get("POLLING_MINUTES", DEFAULT)

app = Celery("api_poller", include=["api_poller.tasks"])

app.config_from_object("api_poller.celeryconfig")

app.conf.beat_schedule = {
    "poll-external-api-every-minute": {
        "task": "api_poller.tasks.test",
        "schedule": crontab(minute=f"*/{POLLING_MINUTES}"),
    }
}