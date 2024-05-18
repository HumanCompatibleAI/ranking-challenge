"""Advanced scoring example

This example demonstrates:
 - how to use Celery to run multiple scoring task types in parallel
 - how to gracefully handle failures and return partial results
 - fine-grained control over task execution time limits
 - how to include timing information in the results for profiling

Given the flexibility of Celery and Python, there are multiple valid ways to
achieve the above goals. This example is one of many possible implementations.

It is not intended to be prescriptive, and indeed more elegant solutions may
be appropriate for your specific use case.

Note in particular that we make no attempts to use Pydantic models that we
defined in the `tasks.py` module, instead defining separate wrapper dataclasses.
This is the middle ground between the "everything is a dict" approach and the
"everything is a Pydantic model" (leaning on type-based dispatch and validation) approach.
Feel free to use any of these approaches in your own code based on your taste and judgement.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, NamedTuple

from celery import group
from celery.utils import uuid

from tasks import random_scorer, sentiment_scorer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # similar to Celery's log format
)
logger = logging.getLogger(__name__)


"""Maximum duration before we return a partial result set"""
DEADLINE_SECONDS = 1


class ScorerType(Enum):
    """Rich label for the different types of scoring tasks we can run

    This enum also defines the runner function for each type of task.

    Attributes:
        name (str): The name of the task.
        runner (Callable): The function that implements the task logic.

    This functionality may also be rolled into a more heavyweight class,
    possibly in the `tasks.py` module, that can tie together the task label,
    input/output models, and runner function.
    """

    SENTIMENT = (auto(), sentiment_scorer)
    RANDOM = (auto(), random_scorer)

    def __init__(self, id, runner):
        self.id = id
        self.runner = runner

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"


class TaskParams(NamedTuple):
    """Lightweight container for task parameters.

    Typical use case might be to maintain a dict of TaskParams, keyed by task_id;
    this can be used to remember certain attributes of the input so that they
    can be injected into the output, or to group the results by item_id or another attribute.
    """

    scorer_type: ScorerType
    item_id: str


@dataclass
class Timings:
    """Timing information for a task"""

    task_id: str
    sent: float = 0
    enqueued: float = 0
    started: float = 0
    completed: float = 0
    result_received: float = 0
    success: bool = False

    def from_result(self, result: dict, t_start: float):
        """This helper method populates the timings from the result dict"""

        if "t_start" in result:
            self.started = result["t_start"] - t_start
        if "t_end" in result:
            self.completed = result["t_end"] - t_start
        self.result_received = time.time() - t_start
        self.success = True
        return self


@dataclass
class ScoringInput:
    """Input wrapper for scoring task data.

    This is a very simple way to enable different types of scoring tasks to be
    provided in a single list, containing just an explicit type and a data dict.

    Approaches based on type unions and/or Pydantic models are also possible.
    """

    scorer_type: ScorerType
    data: dict[str, Any]


@dataclass
class ScoringOutput:
    """Output wrapper for scoring task results.

    Here we rely on the fact that our sample tasks return similar records.
    As above, more sophisticated approaches are possible, including Pydantic models.
    """

    item_id: str
    scorer_type: ScorerType
    timings: Timings
    score: float = 0.0
    error: str | None = None


def compute_scores(input: list[ScoringInput]) -> list[ScoringOutput]:
    """Task dispatcher/manager.

    Args:
        input (list[ScoringInput]): The list of scoring tasks to run.

    Returns:
        list[ScoringOutput]: The list of scoring results.

    This function orchestrates the execution of multiple scoring tasks in parallel,
    by sending them to Celery and collecting the results. It attempts to minimize overhead,
    gracefully propagate failures and timeouts, and return a partial result set if necessary.

    The following flow is implemented:
    1. Create a list of tasks from the input data, using the supplied scorer_type label
       and the associated `tasks.py` runner defined in the ScorerType enum.
    2. Send the task group to Celery for execution; this minimizes the overhead of task creation.
       - a list of pending tasks is maintained, keyed by task_id
    3. Busy-wait for the results, updating the output list as they arrive. This approach is
       required due to the limitations of Celery's `get` method, which has seconds-level granularity.
    4. If the deadline is reached, return a partial result set; here we also use the pending list to
       explicitly mark the tasks that did not complete in time.

    Timing information is collected for each task both by this driver function and by the tasks
    themselves. We found it useful to include this information in the output for tuning and profiling.
    """

    t_start = time.time()
    tasks = []
    task_params: dict[str, TaskParams] = {}
    for item in input:
        scorer_type = item.scorer_type
        item_id = item.data["item_id"]
        task_id = uuid()
        task_params[task_id] = TaskParams(scorer_type=scorer_type, item_id=item_id)
        tasks.append(scorer_type.runner.s(**item.data).set(task_id=task_id))

    logger.info(f"Sending the task group")
    t_sent = time.time() - t_start
    async_result = group(tasks).apply_async()
    t_enqueued = time.time() - t_start

    output = []

    def placeholder_output(task_id: str) -> ScoringOutput:
        timings = Timings(task_id=task_id, sent=t_sent, enqueued=t_enqueued)
        return ScoringOutput(
            item_id=task_params[task_id].item_id,
            scorer_type=task_params[task_id].scorer_type,
            timings=timings,
        )

    def result_callback(task_id: str, result: dict[str, Any]):
        logger.info(f"Received result for task {task_id}")
        item_output = placeholder_output(task_id)
        if isinstance(result, Exception):
            logger.error(f"Task {task_id} raised an exception: {result}")
            item_output.error = str(result)
        else:
            item_output.timings.from_result(result, t_start)
            item_output.score = result["score"]
        output.append(item_output)

    pending = {result.id: result for result in async_result.results}
    while True:
        if time.time() - t_start > DEADLINE_SECONDS:
            logger.info(f"Timeout error")
            break
        for result_id in list(pending.keys()):
            if pending[result_id].ready():
                result = pending.pop(result_id)
                result_callback(result.id, result.result)
        if len(pending) == 0:
            logger.info(f"Received all results")
            break
        time.sleep(0.02)

    for task_id in pending:
        item_output = placeholder_output(task_id)
        item_output.error = "Timed out waiting for results"
        output.append(item_output)

    logger.info(f"Sending results")
    return output


def group_scores(scores: list[ScoringOutput]) -> dict[str, dict[ScorerType, Any]]:
    """Group the scores by item_id and scorer_type.

    The goal is to get an output that looks like this:
     {
        "1": {
            "SENTIMENT": -0.5423,
            "RANDOM": 0.5
        },
        "2": {
            "SENTIMENT": 0.6705,
            "RANDOM": 0.65
        }
    }

    This can be extended to inject other information from the scoring output (e.g. timing)
    and/or to reformat/regroup the output as needed.
    """

    results_placeholder = {scorer_type.name: None for scorer_type in ScorerType}
    results = {}
    for score in scores:
        results.setdefault(score.item_id, results_placeholder.copy()).update(
            {score.scorer_type.name: score.score}
        )
    return results
