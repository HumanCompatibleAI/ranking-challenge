#Working plan for this: 

# use sample data from the original sample_data file: 

#get data: 
from chat_gpt import ranking_server, caller
from sample_data import data_pull, preprocessing
import sys
 
# adding Folder_2 to the system path
sys.path.insert(0, './examples/chat_gpt')
#
# python preprocess.py
# python data_pull.py -p twitter -n 10000

# same implementation as chat_gpt toy example to get initial rankings 
import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI

from sample_data import NEW_POSTS

load_dotenv()  # if a .env file exists, load environment variables from it

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = Flask(__name__)
CORS(app)


def generate__chatGPT_rankings(items):
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



# use the chat_gpt model results to train the mistral model 

# fine tune the model 

# call upon the model to rank new posts 