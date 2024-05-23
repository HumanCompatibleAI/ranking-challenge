"""Celery app for the scorer worker

It is important to keep the Celery app in a separate module from the tasks
so that it can be imported without the possibly heavyweight task dependencies.
"""

import os
from celery import Celery

BROKER = f"{os.getenv('CELERY_BROKER', 'redis://localhost:6380')}/0"
BACKEND = f"{os.getenv('CELERY_BACKEND', 'redis://localhost:6380')}/0"

app = Celery("scheduler", backend=BACKEND, broker=BROKER)
app.conf.redbeat_redis_url = BROKER
app.conf.beat_scheduler = "redbeat.RedBeatScheduler"
