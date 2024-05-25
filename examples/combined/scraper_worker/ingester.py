import json
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from scraper_worker.persistence import (
    ScraperData,
    ScraperErrors,
    connect_ensure_tables,
    ensure_database,
    persist_data,
    persist_error,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DB_URI = os.getenv("SCRAPER_DB_URI")
assert DB_URI, "SCRAPER_DB_URI environment variable must be set"

app = FastAPI(
    title="Scraper ingester",
    description="Basic API for ingesting results from a scraper.",
    version="0.1.0",
)


@app.on_event("startup")
async def initialize_persistence():
    ensure_database()
    connect_ensure_tables()


class SuccessData(BaseModel):
    content_items: list[dict] = Field(
        description="The content items that were scraped.",
    )


class ErrorData(BaseModel):
    message: str = Field(
        description="The error message if the scrape was unsuccessful.",
    )


class IngestData(BaseModel):
    success: bool = Field(
        description="Whether the scrape was successful.",
    )
    task_id: str = Field(
        description="ID or label that uniquely identifies the scrape task.",
    )
    timestamp: datetime = Field(
        description="The timestamp of the scrape.",
    )
    data: Optional[SuccessData] = Field(default=None)
    error: Optional[ErrorData] = Field(default=None)


@app.post("/data/scraper")
def ingest_scrape_data(data: IngestData):
    if not DB_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SCRAPER_DB_URI not set.",
        )
    if data.success:
        if not data.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Success data missing."
            )
        process_success(data.task_id, data.timestamp, data.data.content_items)
    else:
        if not data.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Error data missing."
            )
        process_error(data.task_id, data.timestamp, data.error.message)


@app.get("/")
def health_check():
    return {"status": "ok"}


def process_success(task_id: str, timestamp: datetime, results: list[dict]):
    logger.info(
        f"Received results for {task_id} completed at {timestamp}: length={len(results)}"
    )
    rows = [
        ScraperData(
            post_id=result["id_str"],
            source_id="twitter",
            task_id=task_id,
            post_blob=json.dumps(result),
        )
        for result in results
    ]
    persist_data(rows)


def process_error(task_id: str, timestamp: datetime, message: str):
    logger.info(f"Received error for {task_id} completed at {timestamp}: {message}")
    persist_error(ScraperErrors(source_id="twitter", task_id=task_id, message=message))
