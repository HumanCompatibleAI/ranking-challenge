"""This is a test harness used in development of the scoring job queue.

It can be used to prototype scoring flows independent of the rest of the
ranking pipeline; it is janky and provided mostly for the convenience of the
PRC dev team; use and modify it freely if you find it helpful.

Add the following to docker-compose in order to use it:


  scorer-temp-test-harness:
    build:
      context: scorer_worker
      dockerfile: Dockerfile.scorer
    volumes:
      - ./scorer_worker:/app
    depends_on:
      - redis
    environment:
      REDIS_CONNECTION_STRING: redis://redis-scorer-queue:6380
    command: uvicorn scorer_test_service:app --host 0.0.0.0 --port 8002
    ports:
      - "8002:8002"
"""

import logging

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # similar to Celery's log format
)
logger = logging.getLogger(__name__)

from tasks import RandomScoreInput, RandomScoreOutput, random_scorer
from tasks import SentimentScoreInput, SentimentScoreOutput, sentiment_scorer
from scorer_advanced import ScorerType, ScoringInput, compute_scores
from scorer_basic import compute_scores as compute_scores_basic

app = FastAPI(
    title="Scoring service",
    description="Basic API for performing post scoring.",
    version="0.1.0",
)

DEADLINE_SECONDS = 1


class ScoringRequest(BaseModel):
    data: list[dict[str, Any]] = Field(description="The data to score")


class ScoringResponse(BaseModel):
    data: list[dict[str, Any]] = Field(description="The scored data")


@app.post("/score")
def score(input: ScoringRequest) -> ScoringResponse:
    logger.info(f"Received scoring request")
    results_placeholder = {scorer_type.name: None for scorer_type in ScorerType}
    job_list = []
    for scorer_type in ScorerType:
        for data in input.data:
            job_list.append(ScoringInput(scorer_type=scorer_type, data=data))
    scores = compute_scores(job_list)
    results = {}
    timings = {}
    for score in scores:
        results.setdefault(score.item_id, results_placeholder.copy()).update(
            {score.scorer_type.name: score.score}
        )
        timings.setdefault(score.item_id, results_placeholder.copy()).update(
            {score.scorer_type.name: score.timings}
        )
    output = []
    for item_id, scores in results.items():
        output.append(
            {"item_id": item_id, "scores": scores, "timings": timings[item_id]}
        )
    return ScoringResponse(data=output)


from scorer_basic import compute_scores as compute_scores_basic


@app.post("/score_basic")
def score_basic(input: ScoringRequest) -> ScoringResponse:
    logger.info(f"Received scoring request")
    data = [RandomScoreInput(**x).model_dump() for x in input.data]
    scores = compute_scores_basic(random_scorer, data)
    # results = {}
    # for score in scores:
    #     results[score["item_id"]] = score["score"]
    # output = []
    # for item_id, scores in results.items():
    #     output.append({"item_id": item_id, "score": score})
    return ScoringResponse(data=scores)


@app.get("/")
def health_check():
    return {"status": "ok"}
