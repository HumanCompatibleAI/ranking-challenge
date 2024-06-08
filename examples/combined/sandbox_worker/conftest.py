import sys
from pathlib import Path

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, parse_dsn
from pytest import MonkeyPatch

TEST_DB_DSN = "postgres://postgres:postgres@localhost:5435/posts_test_db?sslmode=disable"
mp = pytest.MonkeyPatch()
mp.setenv("POSTS_DB_URI", TEST_DB_DSN)

from sandbox_worker.tasks import app as celery_app

pytest_plugins = ("celery.contrib.pytest",)

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "redis://localhost:6380",
        "result_backend": "redis://localhost:6380",
    }


@pytest.fixture
def celery_worker_parameters():
    # type: () -> Mapping[str, Any]
    """Redefine this fixture to change the init parameters of Celery workers.

    This can be used e. g. to define queues the worker will consume tasks from.

    The dict returned by your fixture will then be used
    as parameters when instantiating :class:`~celery.worker.WorkController`.
    """
    return {
        # For some reason this `celery.ping` is not registed IF our own worker is still
        # running. To avoid failing tests in that case, we disable the ping check.
        # see: https://github.com/celery/celery/issues/3642#issuecomment-369057682
        # here is the ping task: `from celery.contrib.testing.tasks import ping`
        "perform_ping_check": False,
    }


@pytest.fixture(scope="session")
def my_celery_app():
    celery_app.conf.task_default_queue = "celery"
    # ^ this is the default queue name used by test workers
    return celery_app
