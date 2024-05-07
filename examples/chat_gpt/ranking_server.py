import json
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse
from sample_data import NEW_POSTS

load_dotenv()  # if a .env file exists, load environment variables from it

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = Flask(__name__)
CORS(app)


def generate_rankings(items):
    prompt = ""
    for i, item in enumerate(items):
        prompt += f"ITEM: {i}:\n{item['text']}\n\n"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": 'You are a helpful assistant that processes text and returns results in JSON format. Reorder the items you are given in terms of their positivity, with the most positive item first, and include your reasoning. Give me a JSON array in the following format: [ {"item_idx": int, "reason": str} ]',
            },
            {
                "role": "user",
                "content": "ITEM 0:\nI love you.\n\nITEM 1:\nI hate you.\n\nITEM 2:\nI am indifferent to you.\nITEM 3:\nI like soup\n\n",
            },
            {
                "role": "assistant",
                "content": '[ {"item_idx": 0, "reason": "The statement is very positive."}, {"item_idx": 3, "reason": "The statement is somewhat positive."}, {"item_idx": 2, "reason": "The statement is neutral."}, {"item_idx": 1, "reason": "The statement is negative."} ]',
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    json_results = response.choices[0].message.content.strip()

    # From the docs
    # Warning: Be cautious when parsing JSON data from untrusted sources. A malicious JSON string may cause the decoder to
    # consume considerable CPU and memory resources. Limiting the size of data to be parsed is recommended.
    results = json.loads(json_results)

    indices = [item["item_idx"] for item in results]
    rankings = [items[i]["id"] for i in indices]

    return rankings


@app.route("/rank", methods=["POST"])  # Allow POST requests for this endpoint
def rank_items():
    post_data = request.json

    # Ensure that the input data is valid as a side-effect. This isn't a best-practice,
    # but it demonstrates how you can use the models for validation even if you're not
    # using them to process any data. But consider using FastAPI since it will do all
    # of this automatically for you.
    RankingRequest(**post_data)

    items = post_data.get("items")

    ranked_ids = generate_rankings(items)

    # Add new posts (not part of the candidate set) to the top of the result
    ranked_ids = [new_post["id"] for new_post in NEW_POSTS] + ranked_ids

    result = {
        "ranked_ids": ranked_ids,
        "new_items": NEW_POSTS,
    }

    RankingResponse(**result)  # ensure that the response is valid as a side-effect

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
