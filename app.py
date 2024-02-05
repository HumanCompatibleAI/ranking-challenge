import nltk
nltk.download('vader_lexicon')
from flask import Flask, request, jsonify
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)
analyzer = SentimentIntensityAnalyzer()

@app.route('/')
def index():
    return 'Welcome to Sentiment Analysis API'

@app.route('/analyze_sentiment', methods=['POST'])  # Allow POST requests for this endpoint
def analyze_sentiment():
    data = request.json
    ranked_results = []

    for item in data:
        text = item['text']
        scores = analyzer.polarity_scores(text)
        sentiment = 'positive' if scores['compound'] > 0 else 'negative' if scores['compound'] < 0 else 'neutral'
        ranked_results.append({'text': text, 'sentiment': sentiment, 'scores': scores})

    ranked_results.sort(key=lambda x: x['scores']['compound'], reverse=True)
    return jsonify(ranked_results)

if __name__ == '__main__':
    app.run(debug=True)
