"""Basic scoring example

This example demonstrates how to use Celery to run multiple scoring tasks in parallel.

It is a straightforward application of the Celery's group task primitive, and can be
adequate for simple use cases. The following limitations apply:
- only one result task type can be run by `compute_scores`
- the deadline for the task group is handled by Celery, and therefore has a granularity
  of seconds (i.e. if the deadline is set to 1.5 seconds, it will be rounded up to 2 seconds)
- we return results in an all-or-nothing fashion, i.e. if one task fails, the whole group
  is considered failed, similarly with timeouts
- inputs and outputs are simple Python dicts; you might want to prefer types that
  provide better validation and documentation, such as Pydantic models

Consult the `scorer_advanced.py` example for a more sophisticated approach.
"""

import logging
import time
from typing import Any

from celery import group
from celery.exceptions import TimeoutError
from celery.utils import uuid

from scorer_worker.celery_app import app as celery_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # similar to Celery's log format
)
logger = logging.getLogger(__name__)


# Unfortunately Celery timeout granularity is in seconds, and if this value is
# fractional, it will be rounded up to the nearest second when used in
# `get` with the `timeout` parameter.
DEADLINE_SECONDS = 1


def compute_scores(task_name: str, input: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Task dispatcher/manager.

    Args:
        runner (Callable): The function that implements the task logic (from `tasks.py`).
        input (list[dict[str, Any]]): List of input dictionaries for the tasks.

    Returns:
        list[dict[str, Any]]: List of output dictionaries for the tasks.
    """

    tasks = []
    for item in input:
        tasks.append(celery_app.signature(task_name, kwargs=item, options={"task_id": uuid()}))

    logger.info("Sending the task group")
    async_result = group(tasks).apply_async()
    finished_tasks = []
    start = time.time()
    try:
        # if the tasks are very quick, you can try reducing the interval parameter
        # to get higher polling frequency
        finished_tasks = async_result.get(timeout=DEADLINE_SECONDS, interval=0.1)
    except TimeoutError:
        logger.error(f"Timed out waiting for results after {time.time() - start} seconds")
    except Exception as e:
        logger.error(f"Task runner threw an error: {e}")

    logger.info(f"Finished tasks: {len(finished_tasks)}")
    return finished_tasks
