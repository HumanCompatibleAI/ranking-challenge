from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse
from ranking_challenge.grafana_metrics_middleware import GrafanaMetricsMiddleware
from sample_data import NEW_POSTS
import random

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stdout)

# Create a logger for your ranker
logger = logging.getLogger('ranker')

# Set the level for the ranking_challenge logger (which includes the middleware)
logging.getLogger('ranking_challenge').setLevel(logging.DEBUG)

app = FastAPI(
    title="Prosocial Ranking Challenge ranker development example",
    description="Reorders ranking results and logs custom metrics for development purposes.",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["HEAD", "OPTIONS", "GET", "POST"],
    allow_headers=["*"],
)


# Initialize the Grafana Metrics Middleware
TEAM_ID = "development-shuffle"
metrics_middleware = GrafanaMetricsMiddleware(app, team_id=TEAM_ID)
logger.debug(f"Initialized GrafanaMetricsMiddleware with team_id: {TEAM_ID}")

@app.post("/rank")
async def rank(fastapi_req: Request) -> RankingResponse:
    ranking_request = RankingRequest.model_validate_json(await fastapi_req.body())
    ranked_ids = [content.id for content in ranking_request.items]

    # Log the number of items received
    metrics_middleware.add_custom_metric("items_received", len(ranked_ids), "Number of items received")

    # Randomly choose a ranking behavior
    behavior = random.choice(["shuffle", "reverse", "delete_random", "insert_new"])

    if behavior == "shuffle":
        random.shuffle(ranked_ids)
    elif behavior == "reverse":
        ranked_ids = list(reversed(ranked_ids))
    elif behavior == "delete_random":
        if ranked_ids:
            del ranked_ids[random.choice(range(len(ranked_ids)))]
    elif behavior == "insert_new":
        new_post = NEW_POSTS[ranking_request.session.platform][0]
        ranked_ids.insert(random.randint(0, len(ranked_ids)), new_post["id"])

    # Log the chosen behavior
    metrics_middleware.add_custom_metric(f"behavior_{behavior}", 1, f"Count of {behavior} behavior")

    # Log the final number of items
    metrics_middleware.add_custom_metric("items_returned", len(ranked_ids), "Number of items returned")

    result = {
        "ranked_ids": ranked_ids,
    }

    if behavior == "insert_new":
        result["new_items"] = [
            {
                "id": new_post["id"],
                "url": new_post["url"],
            }
        ]

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)