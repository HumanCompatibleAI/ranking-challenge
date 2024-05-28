import argparse
import inspect
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from itertools import cycle, islice
from typing import Optional

from normalize_posts import NORMALIZED_DATA_FILE_FN
from ranking_challenge.request import ContentItem, RankingRequest, Session
from user_pool import FeedParams, User, UserPool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

platforms = ["facebook", "reddit", "twitter"]


def make_random_user_session(platform, username=None, seed_no=None) -> Session:
    return User.generate_random(platform, username, seed_no).get_session(
        platform, datetime.now()
    )


def count_lines_by_platform():
    line_counts = {}
    for platform in platforms:
        with open(NORMALIZED_DATA_FILE_FN(platform), "r", encoding="utf-8") as f:
            line_counts[platform] = sum(1 for _ in f)
    return line_counts


def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


class UserFeedBuilder:
    def __init__(
        self, user: User, feed_params: FeedParams, feed_end_jitter_hours=12, seed=None
    ):
        random.seed(seed)
        self.user = user
        self.feed_params = feed_params
        now = datetime.now()
        self.is_inactive = (
            user.activity_level == 0 or feed_params.baseline_sessions_per_day == 0
        )
        self.dt_days = 0
        feed_end = now - timedelta(hours=feed_end_jitter_hours * random.random())
        self.last_session_timestamp = feed_end

    def make_request(
        self, platform: str, items_batch: list[ContentItem]
    ) -> RankingRequest:
        if self.is_inactive:
            raise ValueError("Inactive user")
        session_interval = (
            1 / self.user.activity_level / self.feed_params.baseline_sessions_per_day
        )
        self.last_session_timestamp -= timedelta(days=session_interval)
        item_timestamp = self.last_session_timestamp - timedelta(days=session_interval)
        dt = session_interval / len(items_batch)
        for item in items_batch:
            item.created_at = item_timestamp
            item_timestamp += timedelta(days=dt)
        return RankingRequest(
            session=self.user.get_session(platform, self.last_session_timestamp),
            items=items_batch,
        )


def _make_feed(platform, users, items, feed_params, seed=None) -> list[RankingRequest]:
    feed = []
    feed_builders = filter(
        lambda x: not x.is_inactive,
        [UserFeedBuilder(user, feed_params) for user in users],
    )
    # we assume that the items are ordered chronlolgically; since we are building
    # the feed in reverse chronological order, we need to reverse the items
    max_activity = max(feed_params.activity_distribution.keys())
    ibatch = batched(reversed(items), feed_params.items_per_session)
    round_robin_users = cycle(feed_builders)
    random.seed(seed)
    try:
        while True:
            builder = next(round_robin_users)
            relative_activity = builder.user.activity_level / max_activity
            if random.random() > relative_activity:
                continue
            feed.append(builder.make_request(platform, next(ibatch)))
    except StopIteration:
        return sorted(feed, key=lambda x: x.session.current_time)


def bulk_feed_generator(
    feed_params: Optional[FeedParams] = None, seed=None
) -> list[RankingRequest]:
    """
    The purpose of this function is to generate a bulk feed for all platforms.

    We use the UserPool class to generate a pool of users and their respective sessions
    based on feed parameters (sessions per day, items per session, etc).

    In this flow, we fake the timestamps of the sessions to simulate a set of
    sessions that are spread out over a period of time and yield the expected number
    of items in a way that uses up the available content, with the last session
    taking place at the current time.

    When `feed_params` is omitted, we generate a single 'superfeed' that
    nominally represents a feed for a single user and comprises of a mix of
    posts and comments from all platforms over all time.
    """
    feed_list = []
    if feed_params is None:
        # generate "superfeed" for a single dummy user
        for platform in platforms:
            session = make_random_user_session(platform, "test_user")
            with open(NORMALIZED_DATA_FILE_FN(platform), "r", encoding="utf-8") as f:
                feed = [ContentItem.model_validate_json(line) for line in f]
                feed_list.append(RankingRequest(session=session, items=feed))
        return feed_list

    # generate feed for a user pool
    user_pool = UserPool(feed_params, seed=seed)
    platform_users = user_pool.by_platform()
    for platform in platforms:
        users = platform_users[platform]
        with open(NORMALIZED_DATA_FILE_FN(platform), "r", encoding="utf-8") as f:
            items = [ContentItem.model_validate_json(line) for line in f]
            feed_list.extend(_make_feed(platform, users, items, feed_params, seed=seed))

    return feed_list


def random_user_feed_generator(platform, x, seed_no, username):
    """
    This function seeks to convert our sample data into the appropriate JSON format
    that imitates a user's feed for the given platform.

    Args:
    Platform -> String : ['Facebook', 'Reddit', 'Twitter']
    x -> Int
    seed_no -> Int
    username -> String
    """
    if platform.upper() not in (name.upper() for name in platforms):
        print("Not an applicable platform. Try again")
        return

    random.seed(seed_no)
    session = make_random_user_session(platform, username, seed_no)

    with open(NORMALIZED_DATA_FILE_FN(platform), "r", encoding="utf-8") as f:
        feed_sample = random.sample(
            [ContentItem.model_validate_json(line) for line in f], x
        )
        request = RankingRequest(session=session, items=feed_sample)
        print(request.model_dump_json(indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample data from platforms")
    parser.add_argument("-p", "--platform", type=str, help="Platform to pull data from")
    parser.add_argument(
        "-n",
        "--numposts",
        type=int,
        help="number of posts to generate",
        nargs="?",
        default=100,
    )
    parser.add_argument(
        "-r", "--randomseed", type=int, help="random seed", nargs="?", default=None
    )
    parser.add_argument(
        "-u", "--username", type=str, help="username", nargs="?", default=None
    )
    args = parser.parse_args()

    random_user_feed_generator(
        args.platform, args.numposts, args.randomseed, args.username
    )
