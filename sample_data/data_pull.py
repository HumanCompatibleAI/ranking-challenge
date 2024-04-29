import sys
import os
import inspect
import logging
import argparse
import hashlib
import random
import string
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from normalize_posts import NORMALIZED_DATA_FILE_FN

from examples.models.request import RankingRequest, ContentItem, Session

platforms = ['facebook', 'reddit', 'twitter']

def make_random_user_session(platform, username=None, seed_no=None) -> Session:
    random.seed(seed_no)
    if username is None:
        username = ''.join(
            random.choices(string.ascii_lowercase, k=8) +
            random.choices(string.digits, k=3)
        )
    hashed_user = hashlib.sha256(username.encode()).hexdigest()
    # let's make user id deterministic from username
    salt = b"9vB8nz93vD5T7Khw"
    user_id = hashlib.sha256(username.encode() + salt).hexdigest()
    return Session(
        user_id=user_id,
        user_name_hash=hashed_user,
        cohort="XX",
        platform=platform,
        current_time=datetime.now(),
    )


def bulk_feed_generator() -> list[RankingRequest]:
    '''
    The purpose of this function is to generate a bulk feed for all platforms.

    With the completion of https://www.pivotaltracker.com/story/show/187494488
    it will utilize the user pool functionality to imitate feeds for multiple users.

    Currently, we generate a single 'superfeed' that nominally represents a feed for a single user
    and comprises of a mix of posts and comments from all platforms over all time.
    '''
    feed_list = []
    for platform in platforms:
        session = make_random_user_session(platform, 'test_user')
        with open(NORMALIZED_DATA_FILE_FN(platform), 'r') as f:
            feed = [ContentItem.model_validate_json(line) for line in f]
            feed_list.append(RankingRequest(
                session=session,
                items=feed
            ))
    return feed_list


def random_user_feed_generator(platform, x, seed_no, username):
    '''
    This function seeks to convert our sample data into the appropriate JSON format
    that imitates a user's feed for the given platform.

    Args:
    Platform -> String : ['Facebook', 'Reddit', 'Twitter']
    x -> Int
    seed_no -> Int
    username -> String
    '''
    if platform.upper() not in (name.upper() for name in platforms):
        print("Not an applicable platform. Try again")
        return

    random.seed(seed_no)
    session = make_random_user_session(platform, username, seed_no)

    with open(NORMALIZED_DATA_FILE_FN(platform), 'r') as f:
        feed_sample = random.sample([ContentItem.model_validate_json(line) for line in f], x)
        request = RankingRequest(
            session=session,
            items=feed_sample
        )
        print(request.model_dump_json(indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample data from platforms')
    parser.add_argument('-p', '--platform', type=str, help='Platform to pull data from')
    parser.add_argument('-n', '--numposts', type=int, help='number of posts to generate', nargs='?', default=100)
    parser.add_argument('-r', '--randomseed', type=int, help='random seed', nargs='?', default=None)
    parser.add_argument('-u', '--username', type=str, help='username', nargs='?', default=None)
    args = parser.parse_args()

    random_user_feed_generator(args.platform, args.numposts, args.randomseed, args.username)
