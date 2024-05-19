"""Celery app for the scorer worker

It is important to keep the Celery app in a separate module from the tasks
so that it can be imported without the possibly heavyweight task dependencies.
"""

import os
from celery import Celery

BROKER = f"{os.getenv('SCORER_QUEUE_BROKER', 'redis://localhost:6380')}/0"
BACKEND = f"{os.getenv('SCORER_QUEUE_BACKEND', 'redis://localhost:6380')}/0"
app = Celery("scorer_worker", backend=BACKEND, broker=BROKER)
app.autodiscover_tasks(["scorer_worker.tasks"])
