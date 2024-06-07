import requests
import time
import random
import pandas as pd

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
def generate_content(platform):
    selected_rows = {}
    df = SAMPLES.get(platform)
    
    selected_indices = selected_rows.get(platform, [])
    filtered_df = df[~df.index.isin(selected_indices)]
    
    next_row = filtered_df.iloc[0] if not filtered_df.empty else None
    
    # Update selected_rows dictionary
    if next_row is not None:
        selected_indices.append(next_row.name)
        selected_rows[platform] = selected_indices
    
    return next_row.to_json()

