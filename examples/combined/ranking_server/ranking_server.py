import json
import logging
import os
from concurrent.futures.thread import ThreadPoolExecutor

import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse
from scorer_worker.scorer_basic import compute_scores as compute_scores_basic

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%f",
)
logger = logging.getLogger(__name__)
logger.info("Starting up")

REDIS_DB = f"{os.getenv('REDIS_CONNECTION_STRING', 'redis://localhost:6379')}/0"

app = FastAPI(
    title="Prosocial Ranking Challenge combined example",
    description="Ranks input based on how unpopular the things and people in it are.",
    version="0.1.0",
)

# Set up CORS. This is necessary if calling this code directly from a
# browser extension, but if you're not doing that, you won't need this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["HEAD", "OPTIONS", "GET", "POST"],
    allow_headers=["*"],
)

memoized_redis_client = None


def redis_client():
    global memoized_redis_client
    if memoized_redis_client is None:
        memoized_redis_client = redis.Redis.from_url(REDIS_DB)
    return memoized_redis_client


# Straw-man fake hypothesis for why this ranker example is worthwhile:
# Paying too much attention to popular things or people makes a user sad.
# So let's identify the popular named entities in the user's feeds and
# down-rank anything with text that contains them. Then maybe they
# will be less sad.
@app.post("/rank")
def rank(ranking_request: RankingRequest) -> RankingResponse:
    logger.info("Received ranking request")
    ranked_results = []
    # get the named entities from redis
    result_key = "my_worker:scheduled:top_named_entities"

    top_entities = []
    cached_results = redis_client().get(result_key)
    if cached_results is not None:
        top_entities_record = json.loads(cached_results.decode("utf-8"))
        top_entities = set(x[0] for x in top_entities_record["top_named_entities"])

    for item in ranking_request.items:
        score = -1 if any(ne in item.text for ne in top_entities) else 1
        ranked_results.append({"id": item.id, "score": score})

    ranked_results.sort(key=lambda x: x["score"], reverse=True)

    ranked_ids = [content["id"] for content in ranked_results]

    result = {
        "ranked_ids": ranked_ids,
    }
    with ThreadPoolExecutor() as executor:
        data = [{"item_id": x.id, "text": x.text} for x in ranking_request.items]
        future = executor.submit(
            compute_scores_basic, "scorer_worker.tasks.sentiment_scorer", data
        )
        try:
            # logger.info("Submitting score computation task")
            scoring_result = future.result(timeout=0.5)
        except TimeoutError:
            logger.error("Timed out waiting for score results")
        except Exception as e:
            logger.error(f"Error computing scores: {e}")
        else:
            logger.info(f"Computed scores: {scoring_result}")

    return RankingResponse(**result)
