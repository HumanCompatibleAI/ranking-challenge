import hashlib
import json
import logging
import os
import random
import sys
from datetime import datetime
from typing import Callable, Literal

import pandas as pd
from normalize_posts import (
    NORMALIZED_DATA_FILE_FN,
    process_facebook,
    process_reddit,
    process_twitter,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


FB_DATA_FILE = "facebook_data/processed/filtered_comment_post.csv"
REDDIT_DATA_FILE = "reddit_data/processed/filtered_reddit_data.csv"
TWITTER_DATA_FILE = "twitter_data/processed/filtered_jan_2023.json"


platform_filtered_data = {
    "facebook": FB_DATA_FILE,
    "reddit": REDDIT_DATA_FILE,
    "twitter": TWITTER_DATA_FILE,
}

platform_data_gen: dict[Literal["facebook", "reddit", "twitter"], Callable] = {
    "facebook": process_facebook,
    "reddit": process_reddit,
    "twitter": process_twitter,
}


def normalize_data(platform, data_file):
    return platform_data_gen[platform](data_file=data_file)


# Hashing function to anonymise certain data points


def hashed(x):
    """
    This function will hash the respective arg using SHA-256.

    It converts x into a string, then applies a SHA-256 Hash object to it

    """
    try:
        if pd.isna(x):
            return None
        added_salt = os.urandom(16)
        stringed = str(x).encode() + added_salt
        hash_object = hashlib.sha256()
        hash_object.update(stringed)
        return hash_object.hexdigest()
    except Exception:
        return None


SALT = b"9vB8nz93vD5T7Khw"


def static_hashed(x):
    """
    This function will hash the respective arg using SHA-256 with a consistent salt,
    making the hash output consistent for the same input values.

    This is necessary for matching post_ids and ids across posts and comments
    """
    try:
        if pd.isna(x):
            return None
        stringed = str(x).encode() + SALT
        hash_object = hashlib.sha256()
        hash_object.update(stringed)
        return hash_object.hexdigest()
    except Exception:
        return None


# REDDIT PREPROCESSING

# This will get the directory in our git
reddit_relative_path = "reddit_data/raw/reddit_final_data.csv"
script_dir = os.path.dirname(__file__)
reddit_file_path = os.path.join(script_dir, reddit_relative_path)
reddit_data = pd.read_csv(reddit_file_path, low_memory=False).reset_index()

# Split into posts and comments DataFrames
posts_df = reddit_data[reddit_data["type"] == "Post"].copy()
comments_df = reddit_data[reddit_data["type"] == "Comment"].copy()

# Randomly assign comments to posts
post_ids = posts_df["id"].tolist()
comments_df["post_id"] = [random.choice(post_ids) for _ in range(len(comments_df))]
reddit_data = pd.concat([posts_df, comments_df], ignore_index=True)

# Columns hashed
hash_col = ["parent_id", "author"]
for col in hash_col:
    reddit_data[col] = reddit_data[col].apply(hashed)

hash_col = ["id", "post_id"]
for col in hash_col:
    reddit_data[col] = reddit_data[col].apply(static_hashed)

# Convert time to str
for item in reddit_data["created_utc"]:
    item = str(item)

# Rename columns and merge text (comment text) and selftext (post text) column
reddit_data.rename(
    columns={
        "ups": "upvotes",
        "created_utc": "created_at",
        "downs": "downvotes",
        "body": "text",
        "author": "author_name_hash",
    },
    inplace=True,
)
reddit_data["text"] = reddit_data["text"].combine_first(reddit_data["selftext"])

# Lastly, we select relevant columns and then export to a csv within the 'processed' folder
filtered_reddit = reddit_data[
    [
        "id",
        "title",
        "parent_id",
        "post_id",
        "text",
        "author_name_hash",
        "type",
        "created_at",
        "upvotes",
        "downvotes",
        "score"
    ]
]
filtered_reddit.to_csv(os.path.join(script_dir, REDDIT_DATA_FILE), index=False)

# FACEBOOK PREPROCESSING

# This will get the directory in our git
fb_comment_relative_path = "facebook_data/raw/fb_news_comments.csv"
fb_post_relative_path = "facebook_data/raw/fb_news_posts.csv"
script_dir = os.path.dirname(__file__)
comment_file_path = os.path.join(script_dir, fb_comment_relative_path)
post_file_path = os.path.join(script_dir, fb_post_relative_path)
comments = pd.read_csv(comment_file_path)
posts = pd.read_csv(post_file_path)


# We need to split our columns to isolate comment and post post_ids
comments["type"] = "Comment"
posts["type"] = "Post"
comments[["from_id", "c_post_id"]] = comments["post_name"].str.split("_", expand=True)
posts[["post_name", "p_post_id"]] = posts["post_id"].str.split("_", expand=True)

merged = pd.concat([posts, comments], axis=0, ignore_index=True)
assert merged.index.is_unique
# To create author_ids, we will need to use from_id for comments and page_id from posts
merged["author_name_hash"] = merged["page_id"].combine_first(merged["from_id"])
merged["all_post_ids"] = merged["p_post_id"].combine_first(merged["c_post_id"])
merged["parent_id"] = None

# For posts, we need to count the number of comments and drop duplicates
merged = merged.drop_duplicates(subset=["message", "c_post_id"])
comments_count = merged[merged["type"] == "Comment"]["c_post_id"].value_counts().reset_index()
comments_count.columns = ["all_post_ids", "comments_count"]

# We then merge this back to the dataframe and replace NaN with 0 and comment counts for comments to 0
merged = pd.merge(merged, comments_count, on="all_post_ids", how="left")
merged["comments_count"] = merged.apply(
    lambda row: 0 if row["type"] == "Comment" else row["comments_count"], axis=1
)
merged["comments_count"] = merged["comments_count"].fillna(0)

# We then rename columns
merged = merged.drop(columns=["post_id"]).reset_index()
merged.rename(
    columns={
        "react_haha": "haha",
        "react_like": "like",
        "react_angry": "angry",
        "react_love": "love",
        "react_sad": "sad",
        "react_wow": "wow",
        "created_time": "created_at",
        "message": "text",
        "c_post_id": "post_id",
        "index": "id",
        "comments_count": "comments",
    },
    inplace=True,
)

# For our engagement metrics, we replace NaN values with 0
columns = ["like", "love", "haha", "wow", "sad", "angry", "shares"]
merged.loc[:, columns] = merged[columns].fillna(0)

# There are several erroneous created_at values we must remove and change the data type of
merged["created_at_temp"] = pd.to_datetime(merged["created_at"], errors="coerce")
merged = merged[~pd.isna(merged["created_at_temp"])]
merged["created_at"] = pd.to_datetime(merged["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
for item in merged["created_at"]:
    item = str(item)

# We then hash our columns that require hashing, ensuring that 'id' and 'all_post_ids' are hashed identically
hash_col = ["parent_id", "author_name_hash"]
for col in hash_col:
    merged[col] = merged[col].apply(hashed)

hash_col = ["id", "all_post_ids"]
for col in hash_col:
    merged[col] = merged[col].apply(static_hashed)

# Lastly, we export our data out
filtered_facebook = merged[
    [
        "id",
        "parent_id",
        "all_post_ids",
        "text",
        "author_name_hash",
        "type",
        "created_at",
        "like",
        "love",
        "haha",
        "wow",
        "sad",
        "angry",
        "comments",
        "shares",
    ]
]
filtered_facebook.to_csv(os.path.join(script_dir, FB_DATA_FILE), index=False)


# TWITTER PREPROCESSING
script_dir = os.path.dirname(__file__)

# Our files are quite large and disconnected, so we will join them together
files = ["samp1", "samp2", "samp3", "samp4", "samp5"]
jsons = []

# Our file structure requires little preprocessing here, but will require random assignment of parents later on
for file_name in files:
    file_path = os.path.join(script_dir, f"twitter_data/raw/{file_name}.json")
    with open(file_path, "r", encoding="utf-8") as json_file:
        for line in json_file:
            json_obj = json.loads(line.strip())
            if "data" in json_obj and "includes" in json_obj:
                data_part = json_obj["data"]
                includes = json_obj["includes"]

                # Preprocess ID, author_id, and created_at
                if "id" in data_part:
                    data_part["id"] = hashed(data_part["id"])
                if "author_id" in data_part:
                    data_part["author_id"] = hashed(data_part["author_id"])
                if "created_at" in data_part:
                    created = datetime.strptime(data_part["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data_part["created_at"] = str(created.strftime("%Y-%m-%d %H:%M:%S"))

                # Check for expanded_url
                entities = data_part.get("entities", {})
                urls = entities.get("urls", [])
                expanded_url = urls[0].get("expanded_url", None) if urls else None

                # Extracting user metrics from the first user in includes.users
                users = includes.get("users", [])
                user_metrics = users[0].get("public_metrics", {}) if users else None

                # Only append if expanded_url is not None or user_metrics is not None and has content
                if expanded_url or (user_metrics and any(user_metrics.values())):
                    data_part["expanded_url"] = expanded_url
                    if user_metrics:
                        data_part.update(
                            {
                                "followers_count": user_metrics.get("followers_count", 0),
                                "following_count": user_metrics.get("following_count", 0),
                                "tweet_count": user_metrics.get("tweet_count", 0),
                                "listed_count": user_metrics.get("listed_count", 0),
                            }
                        )
                    jsons.append(data_part)

logger.info("Starting preprocessing")

with open(os.path.join(script_dir, TWITTER_DATA_FILE), "w", encoding="utf-8") as output_file:
    json.dump(jsons, output_file, indent=4)

for platform, data_file in platform_filtered_data.items():
    filename = NORMALIZED_DATA_FILE_FN(platform)
    logger.info(f"Writing {filename}")
    items = normalize_data(platform, data_file)
    with open(filename, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item.model_dump_json() + "\n")

logger.info("Finished preprocessing")
