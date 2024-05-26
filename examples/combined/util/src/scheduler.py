import logging
from hashlib import sha1
from typing import Callable, Iterable, Optional

import redis
from celery import Celery
from celery.schedules import schedule
from redbeat import RedBeatScheduler, RedBeatSchedulerEntry


class ScheduledTask:
    """Scheduled task to run at a given interval.

    Args:
        task (celery task callable): The task to run
        interval_seconds (int): The interval in seconds at which to run the task.
        args (tuple): The arguments to pass to the task
        kwargs (dict): The keyword arguments to pass to the task.
        options (dict): The options arguments to pass to the task.

    The args, kwargs, and options are passed directly to the Celery task signature and
    thus to `apply_async`.
    """

    def __init__(
        self,
        task: Callable,
        *,
        interval_seconds: int,
        args: Iterable,
        kwargs: Optional[dict] = None,
        options: Optional[dict] = None,
    ):
        self.path = task.s().task
        # ^ When providing the task to the scheduler, we need to get its import
        # path string.  One way to do this is to create a signature *without*
        # any args or kwargs and get its task attribute.
        self.args = list(args)
        self.kwargs = kwargs or {}
        self.options = options or {}
        self.interval_seconds = interval_seconds
        self.interval = schedule(run_every=interval_seconds)
        self.str_sig = repr(task.s(*self.args, **self.kwargs))

    def __str__(self):
        return self.str_sig

    @property
    def name(self):
        """
        Returns:
            str: The name of the task

        This property is a string representation of the task signature, which includes
        the task name and arguments.
        """
        return self.str_sig


def clear_old_tasks(app, queue=None, logger=None):
    """Clear old tasks from the scheduler.

    Args:
        app (Celery): The Celery app instance.
        queue (str, optional): The queue to clear tasks from. By default, we use
                            the default queue configured for the app.
    """
    logger = logger or logging.getLogger(__name__)
    if queue is None:
        queue = app.conf.task_default_queue
    _ = RedBeatScheduler(app=app)  # ensure beat config is initialized
    redis_client = redis.Redis.from_url(app.conf["BROKER_URL"])
    key_pattern = f"{app.redbeat_conf.key_prefix}{queue}:*"
    logger.info(f"Clearing old tasks with key pattern {key_pattern}")
    for task_name in redis_client.scan_iter(key_pattern):
        logger.info(f"Deleting task {task_name}")
        redis_client.delete(task_name)


def schedule_tasks(
    app: Celery,
    tasks: list[ScheduledTask],
    *,
    logger: Optional[logging.Logger] = None,
):
    """Schedule a task to run at a given interval.

    Args:
        app (Celery): The Celery app instance.
        tasks (list[ScheduledTask]): The list of task to run
    """
    logger = logger or logging.getLogger(__name__)
    clear_old_tasks(app)
    for task in tasks:
        _schedule_task(app, task, logger=logger)


def _schedule_task(
    app: Celery,
    task: ScheduledTask,
    *,
    logger: Optional[logging.Logger] = None,
):
    logger = logger or logging.getLogger(__name__)
    logger.info(f"Scheduled {task.name}")
    queue = app.conf.task_default_queue
    sig_hashed = sha1(task.name.encode("utf-8")).hexdigest()
    key = f"{queue}:sched_{task.path}_{sig_hashed}_{task.interval_seconds}_sec"
    entry = RedBeatSchedulerEntry(
        key,
        task.path,
        task.interval,
        args=task.args,
        kwargs=task.kwargs,
        options={"queue": app.conf.task_default_queue, **task.options},
        app=app,
    )
    entry.save()
    logger.info(f"Scheduled task {key}")
