import nltk
nltk.download('vader_lexicon')
from flask import Flask, request, jsonify
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
analyzer = SentimentIntensityAnalyzer()

@app.route('/')
def index():
    return 'Welcome to The Pro-Social Ranking Challenge'

@app.route('/analyze_sentiment', methods=['POST'])  # Allow POST requests for this endpoint
def analyze_sentiment():
    data = request.json
    ranked_results = []

    for item in data.get("items"):
        text = item.get("text")
        id = item.get("id")
        scores = analyzer.polarity_scores(text)
        sentiment = 'positive' if scores['compound'] > 0 else 'negative' if scores['compound'] < 0 else 'neutral'
        ranked_results.append({'id': id, 'text': text, 'sentiment': sentiment, 'scores': scores})

    ranked_results.sort(key=lambda x: x['scores']['compound'], reverse=True)
    ranked_ids = [content.get('id', None) for content in ranked_results]


    return jsonify(ranked_ids)

if __name__ == '__main__':
    app.run(port = 5001, debug=True)
