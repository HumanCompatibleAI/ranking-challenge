import random

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse

from sample_data import NEW_POSTS

app = FastAPI(
    title="Prosocial Ranking Challenge ranker development example",
    description="Reorders ranking results in a random way for development purposes.",
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


@app.post("/rank")
async def rank(fastapi_req: Request) -> RankingResponse:
    # Validating the json manually like this allows the request body to be text/plain or
    # application/json. This allows the browser to consider the request "simple" CORS, and
    # skips the preflight OPTIONS request. Doing it this way greatly simplifies working
    # with proxies like cloudfront.
    ranking_request = RankingRequest.model_validate_json(await fastapi_req.body())
    ranked_ids = [content.id for content in ranking_request.items]

    # uncomment one of these to change the ranker behaviora
    # random.shuffle(ranked_ids)
    ranked_ids = list(reversed(ranked_ids))

    # delete one random item
    # del ranked_ids[random.choice(range(len(ranked_ids)))]

    # insert the first new post from the sample data
    # new_post = NEW_POSTS[ranking_request.session.platform][0]
    # ranked_ids.insert(2, new_post["id"])

    result = {
        "ranked_ids": ranked_ids,
        # "new_items": [
        #     {
        #         "id": new_post["id"],
        #         "url": new_post["url"],
        #     }
        # ],
    }

    return result
