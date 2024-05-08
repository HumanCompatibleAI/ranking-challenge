import json
import os

from fastapi import FastAPI
import redis

from fastapi.middleware.cors import CORSMiddleware
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse

from test_data import NEW_POSTS

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
    ranked_results = []
    # get the named entities from redis
    result_key = "my_worker:scheduled:top_named_entities"

    top_entities_record = json.loads(redis_client().get(result_key).decode("utf-8"))
    top_entities = set(top_entities_record["top_named_entities"])

    for item in ranking_request.items:
        score = -1 if any(ne in item.text for ne in top_entities) else 1
        ranked_results.append(
            {"id": item.id, "score": score}
        )

    ranked_results.sort(key=lambda x: x["score"], reverse=True)
    ranked_ids = [content["id"] for content in ranked_results]

    result = {
        "ranked_ids": ranked_ids,
    }

    return result
