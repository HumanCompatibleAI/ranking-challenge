import inspect
import logging
import os
import random
import sys

import numpy as np
import pandas as pd
from ranking_challenge.request import (ContentItem, FacebookEngagements,
                                       RedditEngagements, TwitterEngagements)
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)


script_dir = os.path.dirname(__file__)

platforms = ["facebook", "reddit", "twitter"]


def normalized_data_file_fn(x):
    return f"{x}_data/processed/normalized_posts_{x}.json"


NORMALIZED_DATA_FILE_FN = normalized_data_file_fn

FB_DATA_FILE = "facebook_data/processed/filtered_comment_post.csv"
REDDIT_DATA_FILE = "reddit_data/processed/filtered_reddit_data.csv"
TWITTER_DATA_FILE = "twitter_data/processed/filtered_jan_2023.json"


def process_facebook(
    data_file=FB_DATA_FILE, num_samples=-1, seed=0
) -> list[ContentItem]:
    """
    This function seeks to convert our sample data into the appropriate JSON format.

    The function will order comments to appear after the post they are related to.
    If not related to a post it will append the comment at the end of the chain
    """

    df = pd.read_csv(os.path.join(script_dir, data_file))

    posts = df[df["type"] == "Post"]
    if num_samples > 0:
        posts = posts.sample(n=num_samples, random_state=seed)

    comments_grouped_by_post_id = df[df["type"] == "Comment"].groupby("all_post_ids")

    # Instantiate empty list and set
    final_items = []

    for _, row in tqdm(
        posts.iterrows(), "Processing Facebook posts", total=posts.shape[0]
    ):
        item = row.to_dict()
        item = {k: v if v == v else "" for k, v in item.items()}  # replace NaN with ""

        item["type"] = item["type"].lower()
        item["embedded_urls"] = []

        # General structure for engagement metrics
        engagements = FacebookEngagements(
            **{
                "like": item.pop("like", 0),
                "love": item.pop("love", 0),
                "haha": item.pop("haha", 0),
                "wow": item.pop("wow", 0),
                "sad": item.pop("sad", 0),
                "angry": item.pop("angry", 0),
                "comment": item.pop("comments", 0),
                "share": item.pop("shares", 0),
                "care": 0,
            }
        )
        item["engagements"] = engagements

        # General structure for posts
        item["engagements"] = engagements
        post_id = item.pop("all_post_ids")
        item["id"] = post_id
        final_items.append(ContentItem(**item))
        # processed_post_ids.add(post_id)

        # Include related comments directly after their respective post
        if post_id in comments_grouped_by_post_id.groups:
            related_comments = comments_grouped_by_post_id.get_group(post_id)
            for _, comment_row in related_comments.iterrows():
                comment_item = comment_row.to_dict()
                comment_item = {
                    k: v if v == v else "" for k, v in comment_item.items()
                }  # replace NaN with ""

                comment_item["type"] = comment_item["type"].lower()
                comment_item["embedded_urls"] = []
                comment_item["parent_id"] = ""  # one level of threading for now
                comment_item["engagements"] = FacebookEngagements(
                    **{
                        "like": comment_item.pop("like", 0),
                        "love": comment_item.pop("love", 0),
                        "haha": comment_item.pop("haha", 0),
                        "wow": comment_item.pop("wow", 0),
                        "sad": comment_item.pop("sad", 0),
                        "angry": comment_item.pop("angry", 0),
                        "comment": comment_item.pop("comments", 0),
                        "share": comment_item.pop("shares", 0),
                        "care": 0,
                    }
                )
                comment_item["post_id"] = comment_item.pop(
                    "all_post_ids"
                )  # Rename 'all_post_ids' to 'post_id'
                final_items.append(ContentItem(**comment_item))

    return final_items


def process_twitter(
    data_file=TWITTER_DATA_FILE, num_samples=-1, seed=0
) -> list[ContentItem]:
    """
    This function seeks to convert our sample data into the appropriate JSON format.

    We randomly assign parents to create threads.
    We also include a random chance to break a thread so that we can create a stream of posts
    """

    df = pd.read_json(os.path.join(script_dir, data_file))
    if num_samples > 0:
        df = df.sample(n=num_samples, random_state=seed)

    df = df.reset_index(drop=True)
    df["parent_id"] = [None] * len(df)
    if "followers_count" not in df.columns:
        # fake this if it's not available so that the code below for creating engagements works
        df["followers_count"] = [5] * len(df)

    # We establish a blank dictionary to hold the thread info
    graph = {}

    def check_for_cycle(graph, start, visited=None, stack=None):
        if visited is None:
            visited = set()
        if stack is None:
            stack = set()
        visited.add(start)
        stack.add(start)
        for neighbour in graph.get(start, []):
            if neighbour not in visited:
                if check_for_cycle(graph, neighbour, visited, stack):
                    return True
            elif neighbour in stack:
                return True
        stack.remove(start)
        return False

    # We define this function to assign parents and to randomly break threads and create new ones
    def assign_parents(df):
        ids = df["id"].tolist()
        for idx, post_id in enumerate(ids):
            if (
                random.random() > 0.7
            ):  # 30% chance to start a new thread; adjust as needed
                continue
            possible_parents = ids[:idx]
            while possible_parents:
                parent_id = random.choice(possible_parents)
                if parent_id in graph:
                    graph[parent_id].append(post_id)
                else:
                    graph[parent_id] = [post_id]
                if check_for_cycle(graph, parent_id):
                    graph[parent_id].remove(post_id)
                    possible_parents.remove(parent_id)
                else:
                    df.loc[df["id"] == post_id, "parent_id"] = parent_id
                    break

    assign_parents(df)

    # Our structure for tweets. Without 'posts' as a concept, only one structure is needed
    transformed_data = []

    # Randomisation of engagement metrics (current data is majority zero, this will change if we come across improved data)
    # Randomisation will combine a proportional amount of follower count with a random noise variable on top
    reply_seed = 1
    repost_seed = 2
    like_seed = 3
    quote_seed = 4
    noise_std = 1

    np.random.seed(reply_seed)
    df["simulated_replies"] = (
        round(
            (df["followers_count"] * 0.001)
            + np.random.normal(loc=0, scale=noise_std, size=len(df)),
            0,
        )
        .clip(lower=0)
        .astype(int)
    )
    np.random.seed(repost_seed)
    df["simulated_reposts"] = (
        round(
            (df["followers_count"] * 0.005)
            + np.random.normal(loc=0, scale=noise_std, size=len(df)),
            0,
        )
        .clip(lower=0)
        .astype(int)
    )
    np.random.seed(like_seed)
    df["simulated_likes"] = (
        round(
            (df["followers_count"] * 0.01)
            + np.random.normal(loc=0, scale=noise_std, size=len(df)),
            0,
        )
        .clip(lower=0)
        .astype(int)
    )
    np.random.seed(quote_seed)
    df["simulated_quotes"] = (
        round(
            (df["followers_count"] * 0.005)
            + np.random.normal(loc=0, scale=noise_std, size=len(df)),
            0,
        )
        .clip(lower=0)
        .astype(int)
    )

    # Grab relevant fields
    for _, row in tqdm(df.iterrows(), "Processing Twitter posts", total=df.shape[0]):
        embedded_urls = []
        if row.get("expanded_url", None):
            embedded_urls.append(row["expanded_url"])
        transformed_row = {
            "id": row["id"],
            "parent_id": row.get("parent_id", ""),
            "text": row["text"],
            "embedded_urls": embedded_urls,
            "author_name_hash": row["author_id"],
            "type": "post",
            "created_at": (
                row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if pd.notnull(row["created_at"])
                else ""
            ),
            "engagements": TwitterEngagements(
                **{
                    "comment": row.get("simulated_replies", 0),
                    "retweet": row.get("simulated_reposts", 0),
                    "like": row.get("simulated_likes", 0),
                    "share": 0,
                }
            ),
            # these aren't in the current api spec, but it looks like we could add them
            # "user_metrics": {
            #     "followers": row.get('followers_count', 0),
            #     "following": row.get('following_count', 0),
            #     "tweet_count": row.get('tweet_count', 0),
            #     "listed_count": row.get('listed_count', 0),
            # }
        }
        transformed_data.append(ContentItem(**transformed_row))

    return transformed_data


def process_reddit(
    data_file=REDDIT_DATA_FILE, num_samples=-1, seed=0
) -> list[ContentItem]:
    """
    This function seeks to convert our sample data into the appropriate JSON format.

    Our comments have already been randomly assigned in preprocessing.
    Our function simply orders comments to appear after their assigned post.
    """

    df = pd.read_csv(os.path.join(script_dir, data_file), low_memory=False)

    # split into posts and comments
    posts_df = df[df["type"] == "Post"]
    if num_samples > 0:
        posts_df = posts_df.sample(n=num_samples, random_state=seed)

    # Initialize the list to store final items
    final_items = []

    # index comments by post_id for faster lookups
    comments_df = df[df["type"] == "Comment"]
    comments_df = comments_df.set_index("post_id", drop=False)

    # Iterate through each post in the posts DataFrame
    for _, post_row in tqdm(
        posts_df.iterrows(), "Processing Reddit posts", total=posts_df.shape[0]
    ):
        # General structure for posts
        post_item = post_row.to_dict()
        post_item = {
            k: v if v == v else "" for k, v in post_item.items()
        }  # replace NaN with ""
        if post_item["upvotes"] < 0:
            post_item["upvotes"] = 0
        if post_item["downvotes"] < 0:
            post_item["downvotes"] = 0
        post_item["type"] = post_item["type"].lower()
        post_item["engagements"] = RedditEngagements(
            **{
                "upvote": post_item.pop("upvotes", 0),
                "downvote": post_item.pop("downvotes", 0),
                "comment": 0,
                "award": 0,
            }
        )
        post_item["embedded_urls"] = []
        final_items.append(ContentItem(**post_item))

        # Find and append related comments
        related_comments = comments_df[comments_df["post_id"] == post_item["id"]]
        for _, comment_row in related_comments.iterrows():
            comment_item = comment_row.to_dict()
            comment_item = {
                k: v if v == v else "" for k, v in comment_item.items()
            }  # replace NaN with ""
            if comment_item["upvotes"] < 0:
                comment_item["upvotes"] = 0
            if comment_item["downvotes"] < 0:
                comment_item["downvotes"] = 0

            comment_item.pop("title", None)
            comment_item["engagements"] = RedditEngagements(
                **{
                    "upvote": comment_item.pop("upvotes", 0),
                    "downvote": comment_item.pop("downvotes", 0),
                    "comment": 0,
                    "award": 0,
                }
            )
            comment_item["type"] = comment_item["type"].lower()
            comment_item["embedded_urls"] = []
            final_items.append(ContentItem(**comment_item))

    return final_items
