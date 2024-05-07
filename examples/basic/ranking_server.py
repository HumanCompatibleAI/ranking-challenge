import sys

sys.path.append(".")  # allows for importing from the current directory

import nltk
from flask import Flask, jsonify, request
from flask_cors import CORS
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse
from sample_data import NEW_POSTS

nltk.download("vader_lexicon")

app = Flask(__name__)
CORS(app)
analyzer = SentimentIntensityAnalyzer()


@app.route("/rank", methods=["POST"])  # Allow POST requests for this endpoint
def analyze_sentiment():
    post_data = request.json

    # Ensure that the input data is valid as a side-effect. This isn't a best-practice,
    # but it demonstrates how you can use the models for validation even if you're not
    # using them to process any data. But consider using FastAPI since it will do all
    # of this automatically for you.
    RankingRequest(**post_data)

    ranked_results = []
    for item in post_data.get("items"):
        text = item.get("text")
        id = item.get("id")
        scores = analyzer.polarity_scores(text)
        sentiment = (
            "positive"
            if scores["compound"] > 0
            else "negative" if scores["compound"] < 0 else "neutral"
        )
        ranked_results.append(
            {"id": id, "text": text, "sentiment": sentiment, "scores": scores}
        )

    ranked_results.sort(key=lambda x: x["scores"]["compound"], reverse=True)
    ranked_ids = [content.get("id", None) for content in ranked_results]

    # Add a new post (not part of the candidate set) to the top of the result
    new_post = NEW_POSTS[0]
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

    RankingResponse(**result)  # ensure that the response is valid as a side-effect

    # let flask work with the dict though, since it seems to prefer that
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
