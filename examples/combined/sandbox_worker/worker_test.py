# IMPORTANT: these tests assume the test database has been seeded
#            with raw sample data WITHOUT the user pool (which modifies timestamps)
#            i.e. with `python seed_post_db.py --no-user-pool`
import json
from datetime import UTC, datetime

import psycopg2
import pytest
import redis
from sandbox_worker.tasks import (REDIS_DB, count_top_named_entities,
                                  query_posts_db,
                                  substring_matches_by_platform)


def test_query_posts_db(my_celery_app, celery_worker):
    sql = """
SELECT platform, post_blob FROM posts WHERE created_at BETWEEN '2017-05-31' AND '2017-06-01';
"""
    result = query_posts_db.delay(sql)
    assert result
    assert len(result.get()) > 0


def test_query_posts_db_invalid_sql(my_celery_app, celery_worker):
    sql = """
SELECT foo FROM bar;
"""
    with pytest.raises(psycopg2.errors.UndefinedTable):
        result = query_posts_db.delay(sql)
        result.get()


def test_substring_matches_by_platform(my_celery_app, celery_worker):
    result = substring_matches_by_platform.delay(
        "trump", "2017-05-31", "2017-06-01"
    ).get()
    assert "total_rows" in result.keys()
    assert result["total_rows"] > 0


def test_count_top_named_entities(my_celery_app, celery_worker):
    result_key = "my_worker_test:top_named_entities"
    result = count_top_named_entities.delay(10, "2017-05-31", "2017-06-01", result_key)
    success = result.get()
    assert success
    r = redis.Redis.from_url(REDIS_DB)
    raw_result = r.get(result_key)
    assert raw_result is not None, f"Failed to retrieve result key {result_key}"
    r.delete(result_key)
    assert r.get(result_key) is None, "Failed to delete result"
    top_entities = json.loads(raw_result.decode("utf-8"))  # type:ignore
    assert "top_named_entities" in top_entities.keys()
    assert "timestamp" in top_entities.keys()
    result_time = datetime.fromisoformat(top_entities["timestamp"])
    dt = datetime.now(UTC) - result_time
    assert (
        dt.total_seconds() < 10
    ), f"Result timesteamp {result_time} appears to be stale"
