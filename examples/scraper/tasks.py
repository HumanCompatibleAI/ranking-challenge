import os
from datetime import datetime
from celery import Celery
import asyncio
from twscrape import API, gather
import requests
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from typing import Optional

from ingester import IngestData, SuccessData, ErrorData

REDIS_DB = f"{os.getenv('REDIS_CONNECTION_STRING', 'redis://localhost:6379')}/0"


app = Celery('tasks', backend=REDIS_DB, broker=REDIS_DB)


def send_result(task_id: str, results: list[dict], error: Optional[str] = None):
    results_endpoint = os.getenv('RESULTS_ENDPOINT')
    if not results_endpoint:
        logger.error('RESULTS_ENDPOINT not set, skipping results submission.')
        return
    try:
        if error:
            request = IngestData(
                success=False,
                task_id=task_id,
                timestamp=datetime.now(),
                error=ErrorData(message=error)
            )
        else:
            request = IngestData(
                success=True,
                task_id=task_id,
                timestamp=datetime.now(),
                data=SuccessData(content_items=results)
            )
        response = requests.post(results_endpoint, json=request.model_dump(mode='json'))
        response.raise_for_status()
    except Exception as e:
        logger.error(f'Error submitting results: {e}')


def process_success(task_id: str, results: list[dict]):
    return send_result(task_id, results)


def process_error(task_id: str, message: str):
    return send_result(task_id, [], message)


async def _twitter_search_top(query: str, limit: int = 10) -> list[dict]:
    cookies = os.getenv('TWITTER_SESSION_COOKIE')
    username = os.getenv('TWITTER_USERNAME')
    email = os.getenv('TWITTER_EMAIL')
    if not all([cookies, username, email]):
        raise ValueError('Twitter session cookie, username, and email must be set.')

    api = API()
    await api.pool.add_account(username, 'dummy-pass', email, 'dummy-mail-pass', cookies=cookies) #type: ignore

    tweets = await gather(api.search(query, limit=limit, kv={'product': 'Top'}))
    results = []
    for tweet in tweets:
        results.append(tweet.dict())
    return results


@app.task(bind=True)
def twitter_search_top(self, query: str, limit: int = 10) -> None:
    """Use the Twitter session to search for tweets and return results from
    the "top" section.

    Args:
        query (str): search query to use.
        limit (int): number of results to return.
    """

    task_id = self.request.id
    try:
        results = asyncio.run(_twitter_search_top(query, limit))
        process_success(task_id, results)
    except Exception as e:
        process_error(task_id, str(e))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks for the worker."""
    task_manifest = {
        'twitter_top_musk': {
            'function': twitter_search_top,
            'args': ['elon musk', 10],
        },
        'twitter_top_f1': {
            'function': twitter_search_top,
            'args': ['formula one', 10],
        }
    }
    for task_id, task in task_manifest.items():
        sender.add_periodic_task(300, task['function'].s(*task['args']).set(task_id=task_id), name=task_id)
