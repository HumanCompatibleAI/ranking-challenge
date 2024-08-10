import sys
sys.path.append(".")  # allows for importing from the current directory

import nltk
from flask import Flask, jsonify, request
from flask_cors import CORS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse
from ranking_challenge.grafana_metrics_middleware import GrafanaMetricsMiddleware

from sample_data import NEW_POSTS

nltk.download("vader_lexicon")

app = Flask(__name__)
CORS(app)
analyzer = SentimentIntensityAnalyzer()

# Initialize GrafanaMetricsMiddleware
TEAM_ID = "basic_combined_example"
grafana_middleware = GrafanaMetricsMiddleware(app, team_id=TEAM_ID)

@app.route("/rank", methods=["POST"])
def analyze_sentiment():
    post_data = request.json

    # Ensure that the input data is valid as a side-effect
    RankingRequest(**post_data)

    ranked_results = []
    total_sentiment = 0
    for item in post_data.get("items"):
        text = item.get("text")
        id = item.get("id")
        scores = analyzer.polarity_scores(text)
        sentiment = (
            "positive"
            if scores["compound"] > 0
            else "negative"
            if scores["compound"] < 0
            else "neutral"
        )
        ranked_results.append({"id": id, "text": text, "sentiment": sentiment, "scores": scores})
        total_sentiment += scores["compound"]

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

    # Add custom metrics
    grafana_middleware.add_custom_metric("request_count", 1, "Number of requests processed")
    if ranked_results:
        average_sentiment = total_sentiment / len(ranked_results)
        grafana_middleware.add_custom_metric("average_sentiment", average_sentiment, "Average sentiment score")

    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)