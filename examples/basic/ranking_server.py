import nltk
from flask import Flask, jsonify, request
from flask_cors import CORS
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")

app = Flask(__name__)
CORS(app)
analyzer = SentimentIntensityAnalyzer()


@app.route("/rank", methods=["POST"])  # Allow POST requests for this endpoint
def analyze_sentiment():
    post_data = request.json
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

    return jsonify(ranked_ids)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
