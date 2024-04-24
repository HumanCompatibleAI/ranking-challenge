import os
import sys
import inspect
import random

parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)

from fastapi import FastAPI
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from models.request import RankingRequest
from models.response import RankingResponse
from fastapi_nltk.sample_data import NEW_POSTS
from fastapi.middleware.cors import CORSMiddleware

nltk.download("vader_lexicon")

analyzer = SentimentIntensityAnalyzer()

app = FastAPI(
    title="Prosocial Ranking Challenge nltk example",
    description="Ranks input by sentiment using nltk's VADER sentiment analysis.",
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
def rank(ranking_request: RankingRequest) -> RankingResponse:
    ranked_results = []
    for item in ranking_request.items:
        scores = analyzer.polarity_scores(item.text)
        sentiment = (
            "positive"
            if scores["compound"] > 0
            else "negative" if scores["compound"] < 0 else "neutral"
        )
        ranked_results.append(
            {"id": item.id, "text": item.text, "sentiment": sentiment, "scores": scores}
        )

    ranked_results.sort(key=lambda x: x["scores"]["compound"], reverse=True)
    ranked_ids = [content["id"] for content in ranked_results]

    # Add a random new post (not part of the candidate set) to the top of the result
    new_post = NEW_POSTS[ranking_request.session.platform][random.randint(0, 1)]
    ranked_ids.insert(0, new_post["id"])

    result = {
        "ranked_ids": ranked_ids,
        "new_items": [
            {
                "id": new_post["id"],
                "url": new_post["url"],
            }
        ],
    }

    return result
