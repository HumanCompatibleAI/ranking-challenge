import json
import logging
import os
from collections import Counter
from datetime import UTC, datetime
from typing import Any

import pandas as pd
import psycopg2
import redis
from sandbox_worker.celery_app import app
from sandbox_worker.helpers import extract_named_entities
from sqlalchemy import create_engine
from util.scheduler import ScheduledTask, schedule_tasks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


REDIS_DB = f"{os.getenv('REDIS_CONNECTION_STRING', 'redis://localhost:6379')}/0"
DB_URI = os.getenv("POSTS_DB_URI")
assert DB_URI, "POSTS_DB_URI environment variable must be set"


@app.task
def query_posts_db(query: str) -> list[Any]:
    """Query the posts database and return the results.

    Args:
        query (str): The query to run on the posts database.

    Returns:
        list[Any]: The results of the query. Typically this will be list of lists, where each
                   list represents a row in the database.

    The results of the query are stored in the Celery result backend, which we
    have configured as a Redis database. Great care therefore should be taken
    when using this function with large datasets; it is recommended to use this
    function only in prototyping or when a small result set is explicitly
    guaranteed.
    """
    con = psycopg2.connect(DB_URI)
    try:
        cur = con.cursor()
        cur.execute(query)
        results = cur.fetchall()
    finally:
        con.close()
    return results


@app.task
def substring_matches_by_platform(match: str, from_: str, to: str) -> Any:
    """Count number of posts with an occurrence of a string and aggregate by platform.

    Args:
        match (str): The string to search for in the posts.
        from_ (str): The start date of the time range to search (SQLite timestamp
                     format, e.g. '2023-04-01' or '2023-04-01 14:30:00')
        to (str): The end date of the time range to search (SQLite timestamp
                  format, e.g. '2023-04-01' or '2023-04-01 14:30:00')

    Returns:
        dict with number of occurrences by platform and total number of rows:
        Example:
           {'facebook': 77, 'total_rows': 379}

    This illustrates using Pandas to perform the database query and do aggregation
    and processing. Note also the use of SQLite JSON accessor to extract the text.
    """

    query = f"""
SELECT platform, post_blob->>'text' as text FROM posts WHERE created_at BETWEEN '{from_}' AND '{to}';"""

    # For Postgres, Pandas requires SQLAlchemy engine to connect instead of psycopg2
    engine = create_engine(DB_URI.replace("postgres", "postgresql+psycopg2", 1))
    con = engine.connect()
    try:
        df = pd.read_sql_query(query, con)
        df["contains_match"] = df["text"].apply(lambda x: match in x.lower())
        counts = df[df["contains_match"]].groupby("platform").size()
        summary_statistics = counts.to_dict()
        summary_statistics["total_rows"] = len(df)
        return summary_statistics
    finally:
        con.close()


@app.task
def count_top_named_entities(k: int, from_: str, to: str, result_key: str) -> bool:
    """Use NLTK NER capability to return k top mentioned entities in a time range.

    Args:
        k (int): The number of top entities to return.
        from_ (str): The start date of the time range to search (SQLite timestamp
                     format, e.g. '2023-04-01' or '2023-04-01 14:30:00')
        to (str): The end date of the time range to search (SQLite timestamp
                  format, e.g. '2023-04-01' or '2023-04-01 14:30:00')
        result_key (str): The key to store the result in Redis.

    Returns:
        bool: True if the task was successful.

    This function illustrates how to persist the result of a task in Redis manually
    (as opposed to using the Celery result backend). This is particularly useful when the
    task is run via a periodic scheduler, and the result needs to be accessed by other code.
    """

    query = f"""
SELECT post_blob FROM posts WHERE created_at BETWEEN '{from_}' AND '{to}';"""

    con = psycopg2.connect(DB_URI)
    ne_counter = Counter()
    try:
        cur = con.cursor()
        cur.execute(query)
        post_bodies = [x[0].get("text", "") for x in cur.fetchall()]
        for post_body in post_bodies:
            ne_counter.update(set(extract_named_entities(post_body)))
        r = redis.Redis.from_url(REDIS_DB)
        r.set(
            result_key,
            json.dumps(
                {
                    "top_named_entities": ne_counter.most_common(k),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ),
        )
        return True
    finally:
        con.close()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks for the worker.

    This illustrates running the `count_top_named_entities` task every 5 minutes.
    """
    logger.info("Setting up periodic tasks")
    result_key = "my_worker:scheduled:top_named_entities"
    task = ScheduledTask(
        count_top_named_entities,
        args=(10, "2017-05-31", "2017-06-01", result_key),
        interval_seconds=60,
    )
    schedule_tasks(app, [task], logger=logger)
