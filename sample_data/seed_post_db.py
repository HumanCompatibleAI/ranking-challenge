import sys
import os
import inspect
import logging
import sqlite3
import argparse
from typing import Optional

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

from data_pull import bulk_feed_generator, count_lines_by_platform
from user_pool import FeedParams

from examples.models.request import ContentItem, Session

platforms = ['facebook', 'reddit', 'twitter']

DBNAME = 'sample_posts.db'

def exists_table_post(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
    return cur.fetchone() is not None

def drop_table_posts(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("DROP TABLE posts")
    con.commit()

def create_db(con: sqlite3.Connection):
    sql_create_table = """
CREATE TABLE posts (
  id TEXT PRIMARY KEY,
  session_timestamp TIMESTAMP,
  session_user_id TEXT,
  platform TEXT,
  type TEXT,
  author_name_hash TEXT,
  created_at TIMESTAMP,
  post_blob TEXT
)"""
    sql_create_index = """
CREATE INDEX idx_created_at ON posts(created_at)"""
    cur = con.cursor()
    cur.execute(sql_create_table)
    cur.execute(sql_create_index)
    con.commit()


def as_db_row(metadata: Session, post: ContentItem):
    return {
        'id': post.id,
        'session_timestamp': metadata.current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'session_user_id': metadata.user_id,
        'platform': metadata.platform,
        'type': post.type,
        'author_name_hash': post.author_name_hash,
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'post_blob': post.model_dump_json(),
    }


def insert_rows(con: sqlite3.Connection, dbrows: list[dict]):
    cur = con.cursor()
    cur.executemany("""
INSERT OR REPLACE INTO posts VALUES(
    :id,
    :session_timestamp,
    :session_user_id,
    :platform,
    :type,
    :author_name_hash,
    :created_at,
    :post_blob
)""", dbrows)
    con.commit()

def insert_posts(con: sqlite3.Connection, metadata: Session, posts: list[ContentItem]):
    return insert_rows(con, [as_db_row(metadata, post) for post in posts])


def seed_db(feed_params: Optional[FeedParams], seed=None):
    '''
    This function populates the sqlite table
    '''
    con = sqlite3.connect(DBNAME)
    try:
        create_db(con)
    except sqlite3.OperationalError:
        pass

    logger.info(f'Building sqlite database ({DBNAME})')
    # buffering the rows into memory to speed up the insert
    rows = []
    try:
        for feed in bulk_feed_generator(feed_params, seed=seed):
            rows.extend(as_db_row(feed.session, post) for post in feed.items)
        insert_rows(con, rows)
    finally:
        con.close()
    logger.info(f'Finished building sqlite database ({DBNAME})')

def parse_activity_setting(value):
    return {float(k):float(v) for k, v in (kv.split(':') for kv in value.split(','))} if value else None

def parse_platform_setting(value):
    if value == 'auto':
        return count_lines_by_platform()
    return {k:float(v) for k, v in (kv.split(':') for kv in value.split(','))} if value else None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process feed parameters.')
    parser.add_argument('--n-users', required=False, type=int, default=500)
    parser.add_argument('--baseline-sessions-per-day', required=False, type=int, default=1)
    parser.add_argument('--items-per-session', required=False, type=int, default=10)
    parser.add_argument('--activity-distribution', type=parse_activity_setting, default='1:1')
    parser.add_argument('--platform-distribution', type=parse_platform_setting, default='auto')
    parser.add_argument('-r', '--randomseed', type=int, help='random seed', nargs='?', default=None)
    parser.add_argument('--no-user-pool', action='store_true', help='Disable user pool.')
    table_controls = parser.add_mutually_exclusive_group()
    table_controls.add_argument('--drop-table', action='store_true', help='Drop the table before seeding.')
    table_controls.add_argument('--upsert', action='store_true', help='Upsert into the table.')

    args = parser.parse_args()

    feed_params = FeedParams(
        n_users=args.n_users,
        baseline_sessions_per_day=args.baseline_sessions_per_day,
        items_per_session=args.items_per_session,
        activity_distribution=args.activity_distribution,
        platform_distribution=args.platform_distribution
    )

    if exists_table_post(sqlite3.connect(DBNAME)):
        if args.drop_table:
            drop_table_posts(sqlite3.connect(DBNAME))
        elif args.upsert:
            pass
        else:
            logger.error(f'Table posts already exists. Use --drop-table or --upsert to control behavior.')
            sys.exit(1)

    if args.no_user_pool:
        seed_db(None, seed=args.randomseed)
    else:
        seed_db(feed_params, seed=args.randomseed)
