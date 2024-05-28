import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, parse_dsn
from psycopg2.extras import execute_values

import scraper_worker.sql_statements as my_sql

DuplicateDatabase = psycopg2.errors.lookup("42P04")

DATA_TABLE_NAME = "scraper_data"
ERR_TABLE_NAME = "scraper_errors"

DB_URI = os.getenv("SCRAPER_DB_URI")
assert DB_URI, "SCRAPER_DB_URI environment variable must be set"


def ensure_database():
    parsed_dsn = parse_dsn(DB_URI)
    dbname = parsed_dsn.pop("dbname")
    connection = psycopg2.connect(**parsed_dsn)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE {dbname}".format(dbname=sql.Identifier(dbname))
        )
    except DuplicateDatabase:
        pass
    finally:
        cursor.close()
        connection.close()


def ensure_tables(con: psycopg2.extensions.connection):
    cur = con.cursor()
    ddl_statements = [
        my_sql.POSTGRES_CREATE_TABLE_SCRAPER_DATA.format(table_name=DATA_TABLE_NAME),
        my_sql.POSTGRES_CREATE_INDEXES_SCRAPER_DATA.format(table_name=DATA_TABLE_NAME),
        my_sql.POSTGRES_CREATE_TABLE_SCRAPER_ERR.format(table_name=ERR_TABLE_NAME),
        my_sql.POSTGRES_CREATE_INDEXES_SCRAPER_ERR.format(table_name=ERR_TABLE_NAME),
    ]
    try:
        for statement in ddl_statements:
            cur.execute(statement)
        con.commit()
    finally:
        cur.close()


def connect_ensure_tables():
    con = psycopg2.connect(DB_URI)
    try:
        ensure_tables(con)
    finally:
        con.close


@dataclass
class ScraperData:
    post_id: str
    source_id: str
    task_id: str
    post_blob: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def as_dict(self):
        return asdict(self)


@dataclass
class ScraperErrors:
    source_id: str
    task_id: str
    message: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def as_dict(self):
        return asdict(self)


def insert_rows(
    con: psycopg2.extensions.connection,
    dbrows: list,
    table_name: str,
):
    if not dbrows:
        return

    def nonzero_keys(data):
        return [k for k, v in asdict(data).items() if v is not None]

    cur = con.cursor()
    keys = nonzero_keys(dbrows[0])

    query = sql.SQL(
        """
    INSERT INTO {table} ({fields})
    VALUES %s ON CONFLICT DO NOTHING
    """
    ).format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(",").join(map(sql.Identifier, keys)),
    )
    execute_values(
        cur,
        query,
        [[row[k] for k in keys] for row in [asdict(r) for r in dbrows]],
        template=None,
    )
    con.commit()


def persist_data(data: list[ScraperData]):
    con = psycopg2.connect(DB_URI)
    try:
        insert_rows(con, data, DATA_TABLE_NAME)
    finally:
        con.close()


def persist_error(err: ScraperErrors):
    con = psycopg2.connect(DB_URI)
    try:
        insert_rows(con, [err], ERR_TABLE_NAME)
    finally:
        con.close()
