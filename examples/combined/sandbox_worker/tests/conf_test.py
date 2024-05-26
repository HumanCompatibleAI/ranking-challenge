
import pytest

pytest_plugins = ("celery.contrib.pytest",)

from ..src import celery_app


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
