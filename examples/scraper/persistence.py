import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

DATA_TABLE_NAME = 'scraper_data'
ERRORS_TABLE_NAME = 'scraper_errors'

DB_FILE_PATH = os.getenv('DB_FILE_PATH')


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

def table_exists(con: sqlite3.Connection, table_name: str):
    cur = con.cursor()
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cur.fetchone() is not None


def data_table_create(con: sqlite3.Connection, table_name: str):
    sql_create_table = f"""
CREATE TABLE {table_name} (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  post_id TEXT NOT NULL UNIQUE,
  source_id TEXT,
  task_id TEXT,
  post_blob TEXT NOT NULL
)"""
    sql_create_indexes = f"""
CREATE INDEX idx_created_at ON {table_name}(created_at);
CREATE INDEX idx_post_id ON {table_name}(post_id);
CREATE INDEX idx_source_id ON {table_name}(source_id);
CREATE INDEX idx_task_id ON {table_name}(task_id);
    """
    cur = con.cursor()
    cur.execute(sql_create_table)
    try:
        cur.executescript(sql_create_indexes)
    except sqlite3.OperationalError:
        pass
    con.commit()


def errors_table_create(con: sqlite3.Connection, table_name: str):
    sql_create_table = f"""
CREATE TABLE {table_name} (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  source_id TEXT,
  task_id TEXT,
  message TEXT
)"""
    sql_create_indexes = f"""
CREATE INDEX idx_created_at ON {table_name}(created_at);
CREATE INDEX idx_source_id ON {table_name}(source_id);
CREATE INDEX idx_task_id ON {table_name}(task_id);
    """
    cur = con.cursor()
    cur.execute(sql_create_table)
    try:
        cur.executescript(sql_create_indexes)
    except sqlite3.OperationalError:
        pass
    con.commit()


def insert_data_rows(con: sqlite3.Connection, dbrows: list[ScraperData], table_name: str):
    cur = con.cursor()
    cur.executemany(f"""
INSERT OR REPLACE INTO {table_name} VALUES(
    :id,
    :created_at,
    :post_id,
    :source_id,
    :task_id,
    :post_blob
)""", [row.as_dict() for row in dbrows])
    con.commit()


def insert_errors_rows(con: sqlite3.Connection, dbrows: list[ScraperErrors], table_name: str):
    cur = con.cursor()
    cur.executemany(f"""
INSERT OR REPLACE INTO {table_name} VALUES(
    :id,
    :created_at,
    :source_id,
    :task_id,
    :message
)""", [row.as_dict() for row in dbrows])
    con.commit()


def persist_data(data: list[ScraperData]):
    assert DB_FILE_PATH, 'DB_FILE_PATH environment variable must be set'
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        insert_data_rows(con, data, DATA_TABLE_NAME)
    finally:
        con.close()


def persist_error(err: ScraperErrors):
    assert DB_FILE_PATH, 'DB_FILE_PATH environment variable must be set'
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        insert_errors_rows(con, [err], ERRORS_TABLE_NAME)
    finally:
        con.close()


def ensure_tables():
    assert DB_FILE_PATH, 'DB_FILE_PATH environment variable must be set'
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        if not table_exists(con, DATA_TABLE_NAME):
            data_table_create(con, DATA_TABLE_NAME)
        if not table_exists(con, ERRORS_TABLE_NAME):
            errors_table_create(con, ERRORS_TABLE_NAME)
    finally:
        con.close()

