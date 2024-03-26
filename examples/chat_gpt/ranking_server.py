from openai import OpenAI

client = OpenAI(api_key="YOUR-OPENAI-API-KEY-HERE") #insert your openAI API key here!
from flask import Flask, jsonify, request
from flask_cors import CORS

from sample_data import NEW_POSTS

app = Flask(__name__)
CORS(app)

  # Replace with your actual OpenAI API key

def generate_rankings(items):
    prompt = "Rank the following items based on their emotional valence:\n"
    for item in items:
        prompt += f"{item['text']}\n"

    response = client.completions.create(model= "gpt-3.5-turbo",
    prompt=prompt,
    max_tokens=len(items),
    n=1,
    stop=None)

    rankings = response.choices[0].text.strip().split("\n")
    return rankings

@app.route("/rank", methods=["POST"])  # Allow POST requests for this endpoint
def rank_items():
    post_data = request.json
    items = post_data.get("items")

    ranked_ids = generate_rankings(items)

    # Add new posts (not part of the candidate set) to the top of the result
    ranked_ids = [new_post["id"] for new_post in NEW_POSTS] + ranked_ids

    result = {
        "ranked_ids": ranked_ids,
        "new_items": NEW_POSTS,
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5001, debug=True)