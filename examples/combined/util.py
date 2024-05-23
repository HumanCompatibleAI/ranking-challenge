from celery.schedules import schedule
from redbeat import RedBeatSchedulerEntry, RedBeatScheduler
import redis
import logging


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


def schedule_task(
    app, task, *, interval_seconds, task_args, task_kwargs=None, logger=None
):
    """Schedule a task to run at a given interval.

    Args:
        app (Celery): The Celery app instance.
        task (str): The task to run (as a string signature)
        interval_seconds (int): The interval in seconds at which to run the task.
        task_args (tuple): The arguments to pass to the task
        task_kwargs (dict): The keyword arguments to pass to the task.
    """
    logger = logger or logging.getLogger(__name__)
    clear_old_tasks(app)
    interval = schedule(run_every=interval_seconds)
    queue = app.conf.task_default_queue
    task_name = f"{queue}:sched_{task}_{interval_seconds}_sec"
    entry = RedBeatSchedulerEntry(
        task_name,
        task,
        interval,
        args=task_args,
        kwargs=task_kwargs,
        options={"queue": app.conf.task_default_queue},
        app=app,
    )
    entry.save()
    logger.info(f"Scheduled task {task_name}")
