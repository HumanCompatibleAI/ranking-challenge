# This is a driver script to test the async execution of tasks in tasks.py.
# It is intended to serve as a basis for further experimentation.
# The particlar time range chosen here is arbitrary and can be changed as needed;
# it was selected because it contains a reasonable number of Facebook posts in the sample data.

# It illustrates the typical usage of Celery API to execute tasks asynchronously and retrieve the results.
# Specifically, the tasks are enqueued using the .delay() method, which returns an AsyncResult object.
# In cases where we set the results in Redis explicitly, we can use the redis-py library to retrieve the results
# from the specified key.

import redis
from tasks import REDIS_DB, count_top_named_entities, query_posts_db, substring_matches_by_platform


def get_timerange_posts():
    """Get posts from a specific time range."""

    sql = """
SELECT platform, post_blob FROM posts WHERE created_at BETWEEN '2017-05-31' AND '2017-06-01';
"""
    result = query_posts_db.delay(sql)
    print(result.get()[-5:])


def count_trump_posts():
    """Count the number of posts containing the word 'trump' in a specific time range."""

    result = substring_matches_by_platform.delay("trump", "2017-05-31", "2017-06-01")
    print(result.get())


def top_named_entities():
    """Return top 10 named entities and store in a spcific key in Redis."""

    result_key = "my_worker:top_named_entities"
    result = count_top_named_entities.delay(10, "2017-05-31", "2017-06-01", result_key)
    success = result.get(timeout=10)  # customize timeout or omit it as needed
    if not success:
        print("Task failed or timeout reached")
        return
    r = redis.Redis.from_url(REDIS_DB)
    top_entities = r.get(result_key)
    r.delete(result_key)
    print(top_entities.decode("utf-8"))  # type:ignore


if __name__ == "__main__":
    get_timerange_posts()
    count_trump_posts()
    top_named_entities()
