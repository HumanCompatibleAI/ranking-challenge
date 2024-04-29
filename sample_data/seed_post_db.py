import sys
import os
import inspect
import logging
import sqlite3

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

from data_pull import bulk_feed_generator

from examples.models.request import ContentItem, Session

platforms = ['facebook', 'reddit', 'twitter']

DBNAME = 'sample_posts.db'

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
        'session_timestamp': metadata.current_time,
        'session_user_id': metadata.user_id,
        'platform': metadata.platform,
        'type': post.type,
        'author_name_hash': post.author_name_hash,
        'created_at': post.created_at,
        'post_blob': post.model_dump_json(),
    }


def insert_posts(con: sqlite3.Connection, metadata: Session, posts: list[ContentItem]):
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
)""", [as_db_row(metadata, post) for post in posts])
    con.commit()


def seed_db():
    '''
    This function populates the sqlite table
    '''
    con = sqlite3.connect(DBNAME)
    try:
        create_db(con)
    except sqlite3.OperationalError:
        pass

    logger.info(f"Building sqlite database ({DBNAME})")
    try:
        for feed in bulk_feed_generator():
            insert_posts(con, feed.session, feed.items)
    finally:
        con.close()
    logger.info(f"Finished building sqlite database ({DBNAME})")

if __name__ == "__main__":
    seed_db()
