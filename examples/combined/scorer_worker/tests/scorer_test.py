# This is an integration test to illustrate the functionality of the scoring example.
from itertools import cycle

import pytest
from scorer_worker import (
    TIME_LIMIT_SECONDS,
    RandomScoreInput,
    ScorerType,
    ScoringInput,
    compute_scores,
)
from scorer_worker import compute_scores as compute_scores_basic

sample_posts = [
    "That's horrible",
    "BREAKING NEWS- Active shooter at Bronx Lebanon Hospital in NYC. At least 3 people have been shot and the shooter is still on the loose.The suspect is male wearing a lab coat and possibly armed with a M-16 rifle. There is smoke on the 16th floor and the bomb squad is also on the scene.",
    "Arrest them all they deserve it. Getting scared now. We hate their treasonous actions at our expense",
    "You Russian conmen always act like YOU are losing your minds..She has more integrity in her little finger than your entire, beloved, family trump. LOL... losers..lol...  keep whining, it is so becoming of 'conservatives'..no substance, nothing to support, just whine, lie and distort.. we enjoy your dismay about American life.  haha. 🇺🇸",
    "And the idiots were worried about Hillary's emails.  45 is using an unsecured phone but I guess that's okay.",
]


def datagen(n, task_latency_sec=0):
    items = cycle(sample_posts)
    for i in range(n):
        yield RandomScoreInput(
            item_id=str(i),
            text=next(items),
            sleep=task_latency_sec,
            mean=0.5,
            sdev=0.2,
        ).model_dump()


@pytest.fixture
def sample_data():
    return list(datagen(n=4))


@pytest.fixture
def sample_data_with_timeout():
    data = list(datagen(n=4))
    data[-1]["sleep"] = TIME_LIMIT_SECONDS + 1
    return data


@pytest.fixture
def sample_data_with_exception():
    data = list(datagen(n=4))
    data[0]["raise_exception"] = True
    return data


def test_scoring_jobs(my_celery_app, celery_worker, sample_data):
    data = [ScoringInput(ScorerType.RANDOM, x) for x in sample_data]
    scores = compute_scores(data)
    assert len(scores) == len(data)
    assert all(x.error is None for x in scores)


def test_scoring_jobs_with_timeout(
    my_celery_app, celery_worker, sample_data_with_timeout
):
    data = [ScoringInput(ScorerType.RANDOM, x) for x in sample_data_with_timeout]
    scores = compute_scores(data)
    assert len(scores) == len(data)
    assert not all(x.error is None for x in scores)


def test_scoring_jobs_with_exception(
    my_celery_app, celery_worker, sample_data_with_exception
):
    data = [ScoringInput(ScorerType.RANDOM, x) for x in sample_data_with_exception]
    scores = compute_scores(data)
    assert len(scores) == len(data)
    assert not all(x.error is None for x in scores)


def test_scoring_jobs_basic(my_celery_app, celery_worker, sample_data):
    # print(my_celery_app.control.inspect().registered())
    # ^ uncomment to figure out the names of the registered tasks
    data = sample_data
    # when running pytest from the parent directory of this test,
    # the task name is the following
    scores = compute_scores_basic("scorer_worker.tasks.random_scorer", data)
    assert len(scores) == len(data)
