import argparse
import csv
import inspect
import logging
import os
import sqlite3
import sys
import tempfile
from typing import Optional

import psycopg2
import sql
from psycopg2 import sql as pgsql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, parse_dsn

DuplicateDatabase = psycopg2.errors.lookup("42P04")

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

from data_pull import bulk_feed_generator, count_lines_by_platform
from normalize_posts import NORMALIZED_DATA_FILE_FN
from ranking_challenge.request import ContentItem, Session
from user_pool import FeedParams

platforms = ["facebook", "reddit", "twitter"]

DBNAME = "sample_posts.db"


def ensure_database(db_uri: str):
    parsed_dsn = parse_dsn(db_uri)
    dbname = parsed_dsn.pop("dbname")
    connection = psycopg2.connect(**parsed_dsn)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE {dbname}".format(dbname=pgsql.Identifier(dbname))
        )
    except DuplicateDatabase:
        pass
    finally:
        cursor.close()
        connection.close()


def get_yes_no(prompt="Please enter 'yes' or 'no' [Y/n]: "):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ["", "y", "yes"]:
            return True
        elif answer in ["n", "no"]:
            return False
        print("Invalid input.")


def exists_table_post(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
    return cur.fetchone() is not None


def drop_table_posts(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("DROP TABLE posts")
    con.commit()


def create_db(con: sqlite3.Connection):
    sql_create_table = sql.SQLITE_CREATE_TABLE_POSTS
    sql_create_indexes = sql.SQLITE_CREATE_INDEXES_POSTS
    cur = con.cursor()
    cur.execute(sql_create_table)
    cur.executescript(sql_create_indexes)
    con.commit()


def as_db_row(metadata: Session, post: ContentItem):
    return {
        "id": None,
        "post_id": post.id,
        "session_timestamp": metadata.current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "session_user_id": metadata.user_id,
        "platform": metadata.platform,
        "type": post.type,
        "author_name_hash": post.author_name_hash,
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "post_blob": post.model_dump_json(),
    }


def insert_rows(con: sqlite3.Connection, dbrows: list[dict]):
    cur = con.cursor()
    cur.executemany(
        """
INSERT OR REPLACE INTO posts VALUES(
    :id,
    :post_id,
    :session_timestamp,
    :session_user_id,
    :platform,
    :type,
    :author_name_hash,
    :created_at,
    :post_blob
)""",
        dbrows,
    )
    con.commit()


def insert_posts(con: sqlite3.Connection, metadata: Session, posts: list[ContentItem]):
    return insert_rows(con, [as_db_row(metadata, post) for post in posts])


def seed_db(feed_params: Optional[FeedParams], seed=None):
    """
    This function populates the sqlite table
    """
    con = sqlite3.connect(DBNAME)
    try:
        create_db(con)
    except sqlite3.OperationalError:
        pass

    logger.info(f"Building sqlite database ({DBNAME})")
    # buffering the rows into memory to speed up the insert
    rows = []
    try:
        for feed in bulk_feed_generator(feed_params, seed=seed):
            rows.extend(as_db_row(feed.session, post) for post in feed.items)
        insert_rows(con, rows)
    finally:
        con.close()
    logger.info(f"Finished building sqlite database ({DBNAME})")


def parse_activity_setting(value):
    return (
        {float(k): float(v) for k, v in (kv.split(":") for kv in value.split(","))}
        if value
        else None
    )


def parse_platform_setting(value):
    if value == "auto":
        return count_lines_by_platform()
    return (
        {k: float(v) for k, v in (kv.split(":") for kv in value.split(","))}
        if value
        else None
    )


def ensure_postgres_table(con: psycopg2.extensions.connection):
    cur = con.cursor()
    cur.execute(sql.POSTGRES_CREATE_TABLE_POSTS)  # create table if not exists
    cur.execute(sql.POSTGRES_CREATE_INDEXES_POSTS)  # create indexes if not exists
    cur.execute("""
        SELECT EXISTS(
            SELECT 1
            FROM posts
        );
    """)
    try:
        result = cur.fetchone()
        if result is None:
            raise Exception("Unable to check for table existence.")
        if result[0]:
            if get_yes_no(
                "Postgres table 'posts' already exists and is not empty. Drop it? [Y/n]: "
            ):
                cur.execute("DROP TABLE posts")
                cur.execute(sql.POSTGRES_CREATE_TABLE_POSTS)
                cur.execute(sql.POSTGRES_CREATE_INDEXES_POSTS)
                con.commit()
    finally:
        cur.close()


from pathlib import Path


def copy_sqlite_to_postgres(
    con: psycopg2.extensions.connection, sqlite_con: sqlite3.Connection
):
    # Export table to CSV

    temp_dir = Path(__file__).parent.resolve()
    with tempfile.TemporaryDirectory() as temp_dir:
        filename = "posts.csv"
        cur = sqlite_con.cursor()
        try:
            with open(Path(temp_dir) / filename, "w+", newline="") as temp_csv:
                cur.execute("SELECT * FROM posts")
                csvwriter = csv.writer(
                    temp_csv, escapechar="\\", doublequote=False, quoting=csv.QUOTE_NONE
                )
                csvwriter.writerows(cur.fetchall())
        finally:
            cur.close()

        cur = con.cursor()
        try:
            with open(Path(temp_dir) / filename, "r", newline="") as temp_csv:
                cur.copy_from(temp_csv, "posts", sep=",", null="")
                logger.info("Data copied to postgres.")
        finally:
            cur.close()


def do_seed_postgres(db_uri):
    ensure_database(db_uri)
    con = psycopg2.connect(db_uri)
    sqlite_con = sqlite3.connect(DBNAME)
    try:
        ensure_postgres_table(con)
        copy_sqlite_to_postgres(con, sqlite_con)
    finally:
        con.commit()
        con.close()
        sqlite_con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process feed parameters.")
    parser.add_argument("--n-users", required=False, type=int, default=500)
    parser.add_argument(
        "--baseline-sessions-per-day", required=False, type=int, default=1
    )
    parser.add_argument("--items-per-session", required=False, type=int, default=10)
    parser.add_argument(
        "--activity-distribution", type=parse_activity_setting, default="1:1"
    )
    parser.add_argument(
        "--platform-distribution", type=parse_platform_setting, default="auto"
    )
    parser.add_argument(
        "-r", "--randomseed", type=int, help="random seed", nargs="?", default=None
    )
    parser.add_argument(
        "--no-user-pool", action="store_true", help="Disable user pool."
    )
    parser.add_argument("--dbname", type=str, help="Database file name")
    table_controls = parser.add_mutually_exclusive_group()
    table_controls.add_argument(
        "--drop-table", action="store_true", help="Drop the table before seeding."
    )
    table_controls.add_argument(
        "--upsert", action="store_true", help="Upsert into the table."
    )
    parser.add_argument(
        "--seed-postgres",
        action="store_true",
        help="Copy the SQLite table to postgres. Requires POSTS_DB_URI env var to be set",
    )

    args = parser.parse_args()

    for platform in platforms:
        if not os.path.exists(NORMALIZED_DATA_FILE_FN(platform)):
            logger.error(
                f"Normalized data file for {platform} not found. Please run preprocessing.py first."
            )
            sys.exit(1)

    if args.dbname:
        DBNAME = args.dbname.removesuffix(".db") + ".db"

    db_uri = os.environ.get("POSTS_DB_URI")
    if args.seed_postgres:
        logger.info(f"Performing ETL from {DBNAME} to postgres")
        if not db_uri:
            logger.error("POSTS_DB_URI environment variable not set.")
            sys.exit(1)
        else:
            do_seed_postgres(db_uri)
            sys.exit(0)

    feed_params = FeedParams(
        n_users=args.n_users,
        baseline_sessions_per_day=args.baseline_sessions_per_day,
        items_per_session=args.items_per_session,
        activity_distribution=args.activity_distribution,
        platform_distribution=args.platform_distribution,
    )

    if exists_table_post(sqlite3.connect(DBNAME)):
        if args.drop_table:
            drop_table_posts(sqlite3.connect(DBNAME))
        elif args.upsert:
            pass
        else:
            logger.error(
                "Table posts already exists. Use --drop-table or --upsert to control behavior."
            )
            sys.exit(1)

    if args.no_user_pool:
        seed_db(None, seed=args.randomseed)
    else:
        seed_db(feed_params, seed=args.randomseed)

    if not db_uri:
        logger.warning(
            "POSTS_DB_URI environment variable not set; skipping copying to postgres."
        )
    else:
        do_seed_postgres(db_uri)
