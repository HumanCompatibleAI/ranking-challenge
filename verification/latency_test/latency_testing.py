import json
import random
import time
import argparse
import pandas as pd
import requests
from collections import defaultdict
from fastapi.encoders import jsonable_encoder
from ranking_challenge.fake import fake_request
from ranking_challenge.request import ContentItem, RankingRequest
from tqdm import tqdm
import numpy as np

facebook = pd.read_json('facebook_feed.json')
reddit = pd.read_json('reddit_feed.json')
twitter = pd.read_json('twitter_feed.json')

TARGET_LATENCY = 0.5  # Target latency in seconds (500ms p95)
NUM_REQUESTS = 600   # Number of requests for each platform to generate a statistically valid sample
PLATFORMS = ['Facebook', 'Reddit', 'Twitter']
SAMPLES = {'Facebook' : facebook, 'Reddit' : reddit, 'Twitter': twitter}

results_df = pd.DataFrame(columns=['Platform', 'Latency', 'Num_Items'])

# Generates the next request for the platform by iterating through the
# dataframe for the next sample, and returning it in json format. Goes through
# each dataframe individually
selected_rows = {}
def generate_items(platform):
    selected_rows = {}
    df = SAMPLES.get(platform)

    selected_indices = selected_rows.get(platform, [])
    filtered_df = df[~df.index.isin(selected_indices)]

    next_row = filtered_df.iloc[0] if not filtered_df.empty else None

    # Update selected_rows dictionary
    if next_row is not None:
        selected_indices.append(next_row.name)
        selected_rows[platform] = selected_indices

    content_items = [ContentItem.model_validate(item_df) for item_df in next_row]
    return content_items

def issue_request(platform, url):
    items = generate_items(platform)
    request = fake_request(n_posts=0, n_comments=0, platform=platform.lower())
    request.items = items

    start_time = time.time()
    # application should be running on localhost:8000
    response = requests.post(url, json=jsonable_encoder(request))
    if response.status_code != 200:
        raise Exception('Request failed with status code: {}, error: {}'.format(response.status_code, response.text))

    # Validate response is JSON-parsable
    try:
        json_response = response.json()
    except json.JSONDecodeError as e:
        raise Exception('Response is not JSON parsable: {}'.format(e))
    
    end_time = time.time()
    latency = end_time - start_time

    # Store latency, platform, and number of items in DataFrame
    results_df.loc[len(results_df)] = [platform, latency, len(request.items)]
    return latency

# Main function to run the test
latencies = defaultdict(list)
def run_test(url):
    for platform in PLATFORMS:
        for _ in tqdm(range(NUM_REQUESTS), f"Platform: {platform}"):
            latency = issue_request(platform, url)
            latencies[platform].append(latency)

def check_p95_threshold(results_df):
    latencies = results_df['Latency'].values
    p95_latency = np.percentile(latencies, 95)
    return p95_latency <= TARGET_LATENCY

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ranking challenge test.")
    parser.add_argument("url", help="URL of the application to test")
    args = parser.parse_args()

    run_test(args.url)

    for platform in PLATFORMS:
        passes_95 = check_p95_threshold(results_df.where(results_df['Platform'] == platform))
        if passes_95:
            print(f"All requests pass p95 for {platform}!")
        else:
            print(f"Some requests do not pass p95 for {platform}.")
