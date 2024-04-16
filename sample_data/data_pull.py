# Importing of relevant packages
import numpy as np
import random
import pandas as pd
from pathlib import Path
import os
import sys
import inspect
import hashlib
from datetime import datetime
import json
import argparse

parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)

from examples.models.request import RankingRequest, FacebookEngagements, RedditEngagements, TwitterEngagements, ContentItem

script_dir = os.path.dirname(__file__)

platforms = ['facebook', 'reddit', 'twitter']


def data_puller(platform, x, seed_no, username):
    '''
    This function seeks to convert our sample data into the appropriate JSON format.
    It will download this file to "os.path.dirname(__file__)" under the name 'final_{platform}_data.json'

    Args:
    Platform -> String : ['Facebook', 'Reddit', 'Twitter']
    x -> Int
    seed_no -> Int
    username -> String

    For Facebook data:
    The function will order comments to appear after the post they are related to.
    If not related to a post it will append the comment at the end of the chain

    For Reddit data:
    Our comments have already been randomly assigned in preprocessing.
    Our function simply orders comments to appear after their assigned post.

    For Twitter data:
    We randomly sample a subset of our twitter data and then randomly assign parents to create threads.
    We also include a random chance to break a thread so that we can create a stream of posts

    '''
    if platform.upper() not in (name.upper() for name in platforms):
        print("Not an applicable platform. Try again")

    np.random.seed(seed_no)

    # We must create a hashed user_id and hashed_username
    hasher = hashlib.sha256()
    hasher.update(os.urandom(16))
    user_id = hasher.hexdigest()

    hasher = hashlib.sha256()
    hasher.update(username.encode())
    hashed_user = hasher.hexdigest()

    current_time = str(datetime.now()) # JSON does not accept datetime obj

    # Establish static part of JSON
    static_json = {
        "session": {
            "user_id": user_id,
            "user_name_hash": hashed_user,
            "platform": platform,
            "cohort": "AB",
            "current_time": current_time,
        },
        "items": []
    }

    if platform.upper() == 'FACEBOOK':
        df = pd.read_csv(os.path.join(script_dir, 'facebook_data/processed/filtered_comment_post.csv'))

        # We randomly sample x values and then group our comments by 'all_post_ids'
        posts = df[df['type'] == 'Post'].sample(n=x, random_state=seed_no)
        comments_grouped_by_post_id = df[df['type'] == 'Comment'].groupby('all_post_ids')

        # Instantiate empty list and set
        final_items = []

        for index, row in posts.iterrows():
            item = row.to_dict()
            item = {k: v if v == v else "" for k, v in item.items()}  # replace NaN with ""

            item["type"] = item["type"].lower()
            item["embedded_urls"] = []

            # General structure for engagement metrics
            engagements = FacebookEngagements(**{
                'like': item.pop('like', 0),
                'love': item.pop('love', 0),
                'haha': item.pop('haha', 0),
                'wow': item.pop('wow', 0),
                'sad': item.pop('sad', 0),
                'angry': item.pop('angry', 0),
                'comment': item.pop('comments', 0),
                'share': item.pop('shares', 0),
                'care': 0,
            })
            item['engagements'] = engagements

            # General structure for posts
            item['engagements'] = engagements
            post_id = item.pop('all_post_ids')
            item['id'] = post_id
            final_items.append(ContentItem(**item))
            # processed_post_ids.add(post_id)

            # Include related comments directly after their respective post
            if post_id in comments_grouped_by_post_id.groups:
                related_comments = comments_grouped_by_post_id.get_group(post_id)
                for _, comment_row in related_comments.iterrows():
                    comment_item = comment_row.to_dict()
                    comment_item = {k: v if v == v else "" for k, v in comment_item.items()}  # replace NaN with ""

                    comment_item["type"] = comment_item["type"].lower()
                    comment_item["embedded_urls"] = []
                    comment_item["parent_id"] = ""  # one level of threading for now
                    comment_item["engagements"] = FacebookEngagements(**{
                        'like': comment_item.pop('like', 0),
                        'love': comment_item.pop('love', 0),
                        'haha': comment_item.pop('haha', 0),
                        'wow': comment_item.pop('wow', 0),
                        'sad': comment_item.pop('sad', 0),
                        'angry': comment_item.pop('angry', 0),
                        'comment': comment_item.pop('comments', 0),
                        'share': comment_item.pop('shares', 0),
                        'care': 0,
                    })
                    comment_item['post_id'] = comment_item.pop('all_post_ids')  # Rename 'all_post_ids' to 'post_id'
                    final_items.append(ContentItem(**comment_item))

        static_json['items'] = final_items


    if platform.upper() == 'REDDIT':
        df = pd.read_csv(os.path.join(script_dir,'reddit_data/processed/filtered_reddit_data.csv'), low_memory=False)

        # We will sample from our dataset and then split into posts and comments
        posts_df =  df[df['type'] == 'Post']
        sample = posts_df.sample(n=x, random_state=seed_no)

        # Initialize the list to store final items
        final_items = []

        # Iterate through each post in the posts DataFrame
        for _, post_row in sample.iterrows(): # change made here, was posts_df before
            # General structure for posts
            post_item = post_row.to_dict()
            post_item = {k: v if v == v else "" for k, v in post_item.items()}  # replace NaN with ""
            if post_item['upvotes'] < 0:
                post_item['upvotes'] = 0
            if post_item['downvotes'] < 0:
                post_item['downvotes'] = 0
            post_item["type"] = post_item["type"].lower()
            post_item['engagements'] = RedditEngagements(**{'upvote': post_item.pop('upvotes', 0), 'downvote': post_item.pop('downvotes', 0), 'comment': 0, 'award': 0})
            post_item['embedded_urls'] = []
            final_items.append(post_item)

            # Find and append related comments
            # related_comments = comments_df[comments_df['post_id'] == post_item['id']]
            related_comments = df[(df['type'] == 'Comment') & (df['post_id'] == post_item['id'])]
            for _, comment_row in related_comments.iterrows():
                comment_item = comment_row.to_dict()
                comment_item = {k: v if v == v else "" for k, v in comment_item.items()}  # replace NaN with ""
                if comment_item['upvotes'] < 0:
                    comment_item['upvotes'] = 0
                if comment_item['downvotes'] < 0:
                    comment_item['downvotes'] = 0

                comment_item.pop('title', None)
                comment_item['engagements'] = RedditEngagements(**{'upvote': comment_item.pop('upvotes', 0), 'downvote': comment_item.pop('downvotes', 0), 'comment': 0, 'award': 0})
                comment_item["type"] = comment_item["type"].lower()
                comment_item['embedded_urls'] = []
                final_items.append(comment_item)

        static_json['items'] = final_items

    if platform.upper() == 'TWITTER':
        df = pd.read_json(os.path.join(script_dir,'twitter_data/processed/filtered_jan_2023.json'))

        # We will sample from our dataset and establish an empty parent_id column
        sample = df.sample(n=x, random_state=seed_no).reset_index(drop=True)
        sample['parent_id'] = [None] * len(sample)
        if 'followers_count' not in sample.columns:
            # fake this if it's not available so that the code below for creating engagements works
            sample['followers_count'] = [5] * len(sample)

        # We establish a blank dictionary to hold the thread info
        graph = {}
        def check_for_cycle(graph, start, visited=None, stack=None):
            if visited is None: visited = set()
            if stack is None: stack = set()
            visited.add(start); stack.add(start)
            for neighbour in graph.get(start, []):
                if neighbour not in visited:
                    if check_for_cycle(graph, neighbour, visited, stack): return True
                elif neighbour in stack: return True
            stack.remove(start)
            return False

        # We define this function to assign parents and to randomly break threads and create new ones
        def assign_parents(sample):
            ids = sample['id'].tolist()
            for idx, post_id in enumerate(ids):
                if random.random() > 0.7:  # 30% chance to start a new thread; adjust as needed
                    continue
                possible_parents = ids[:idx]
                while possible_parents:
                    parent_id = random.choice(possible_parents)
                    if parent_id in graph: graph[parent_id].append(post_id)
                    else: graph[parent_id] = [post_id]
                    if check_for_cycle(graph, parent_id):
                        graph[parent_id].remove(post_id)
                        possible_parents.remove(parent_id)
                    else:
                        sample.loc[sample['id'] == post_id, 'parent_id'] = parent_id
                        break

        assign_parents(sample)

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
        sample['simulated_replies'] = round((sample['followers_count'] * 0.001) + np.random.normal(loc=0, scale=noise_std, size=len(sample)), 0).clip(lower=0).astype(int)
        np.random.seed(repost_seed)
        sample['simulated_reposts'] = round((sample['followers_count'] * 0.005) + np.random.normal(loc=0, scale=noise_std, size=len(sample)), 0).clip(lower=0).astype(int)
        np.random.seed(like_seed)
        sample['simulated_likes'] = round((sample['followers_count'] * 0.01) + np.random.normal(loc=0, scale=noise_std, size=len(sample)), 0).clip(lower=0).astype(int)
        np.random.seed(quote_seed)
        sample['simulated_quotes'] = round((sample['followers_count'] * 0.005) + np.random.normal(loc=0, scale=noise_std, size=len(sample)), 0).clip(lower=0).astype(int)

        # Grab relevant fields
        for _, row in sample.iterrows():
            embedded_urls = []
            if row.get("expanded_url", None):
                embedded_urls.append(row["expanded_url"])
            transformed_row = {
                "id": row['id'],
                "parent_id": row.get('parent_id', ''),
                "text": row['text'],
                "embedded_urls": embedded_urls,
                "author_name_hash": row['author_id'],
                "type": 'post',
                "created_at": row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['created_at']) else '',
                "engagements": TwitterEngagements(**{
                    'comment': row.get('simulated_replies', 0),
                    'retweet': row.get('simulated_reposts', 0),
                    'like': row.get('simulated_likes', 0),
                    'share': 0,
                })
                # these aren't in the current api spec, but it looks like we could add them
                # "user_metrics": {
                #     "followers": row.get('followers_count', 0),
                #     "following": row.get('following_count', 0),
                #     "tweet_count": row.get('tweet_count', 0),
                #     "listed_count": row.get('listed_count', 0),
                # }
            }
            transformed_data.append(ContentItem(**transformed_row))

        static_json["items"] = transformed_data

    request = RankingRequest(**static_json)

    # done, output
    print(request.model_dump_json(indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample data from platforms')
    parser.add_argument('-p', '--platform', type=str, help='Platform to pull data from')
    parser.add_argument('-n', '--numposts', type=int, help='number of posts to generate', nargs='?', const=100, default=100)
    parser.add_argument('-r', '--randomseed', type=int, help='random seed', nargs='?', const=1, default=1)
    parser.add_argument('-u', '--username', type=str, help='username', nargs='?', const="username", default="username")
    args = parser.parse_args()

    data_puller(args.platform, args.numposts, args.randomseed, args.username)
