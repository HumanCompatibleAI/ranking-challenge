# Importing of relevant packages
import numpy as np
import random
import pandas as pd
from pathlib import Path
import os
import hashlib
from datetime import datetime
import json
import argparse

script_dir = os.path.dirname(__file__)

platforms = ['facebook', 'reddit', 'twitter']



def data_puller(platform):
    '''
    This function seeks to convert our sample data into the appropriate JSON format.
    It will download this file to "os.path.dirname(__file__)" under the name 'final_{platform}_data.json'

    Args:
    Platform -> String : ['Facebook', 'Reddit', 'Twitter']

    Inputs:
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

    x = int(input(f"Please input how many data points you wish to sample for {platform} (suggested: 50000):"))
    seed_no = int(input("Please input a seed number:"))
    np.random.seed(seed_no)

    username = input("Please select a username to be hashed. This is how we can identify posts authored by the current user:")

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
        "current_time": current_time,
    },
    "items": []
    }

    if platform.upper() == 'FACEBOOK':
        df = pd.read_csv(os.path.join(script_dir, 'facebook_data/processed/filtered_comment_post.csv'))

        # We randomly sample x values and then group our comments by 'all_post_ids'
        sample = df.sample(n=x, random_state=seed_no)
        comments_grouped_by_post_id = sample[sample['type'] == 'Comment'].groupby('all_post_ids')

        # Instantiate empty list and set
        final_items = []
        processed_post_ids = set()

        for index, row in sample.iterrows():
            item = row.to_dict()
            # General structure for engagement metrics
            engagements = {
                'likes': item.pop('like', 0),
                'love': item.pop('love', 0),
                'haha': item.pop('haha', 0),
                'wow': item.pop('wow', 0),
                'sad': item.pop('sad', 0),
                'angry': item.pop('angry', 0),
                'comments': item.pop('comments', 0),
                'shares': item.pop('shares', 0),
            }
            item['engagements'] = engagements

            # General structure for posts
            if item['type'] == 'Post':
                post_id = item.pop('all_post_ids')
                item['id'] = post_id
                item.pop('post_id', None)
                item.pop('parent_id', None)
                final_items.append(item)
                processed_post_ids.add(post_id)

                # Include related comments directly after their respective post
                if post_id in comments_grouped_by_post_id.groups:
                    related_comments = comments_grouped_by_post_id.get_group(post_id)
                    for _, comment_row in related_comments.iterrows():
                        comment_item = comment_row.to_dict()
                        comment_item['post_id'] = comment_item.pop('all_post_ids')  # Rename 'all_post_ids' to 'post_id'
                        final_items.append(comment_item)

        # Append orphan comments (not attached to any processed post) at the end
        for _, comment_row in sample[sample['type'] == 'Comment'].iterrows():
            comment_item = comment_row.to_dict()
            if comment_item.get('all_post_ids') not in processed_post_ids:
                comment_item['post_id'] = comment_item.pop('all_post_ids')  # Ensure 'post_id' is correctly set
                final_items.append(comment_item)

        static_json['items'] = final_items


    if platform.upper() == 'REDDIT':
        df = pd.read_csv(os.path.join(script_dir,'reddit_data/processed/filtered_reddit_data.csv'))

        # We will sample from our dataset and then split into posts and comments
        sample = df.sample(n=x, random_state=seed_no)
        posts_df = sample[sample['type'] == 'Post']
        comments_df = sample[sample['type'] == 'Comment']

        # Initialize the list to store final items
        final_items = []

        # Iterate through each post in the posts DataFrame
        for _, post_row in posts_df.iterrows():
            # General structure for posts
            post_item = post_row.to_dict()
            post_item.pop('parent_id', None)
            post_item.pop('post_id', None)
            post_item.pop('text', None)
            post_item['engagements'] = {'upvotes': post_item.pop('upvotes', 0), 'downvotes': post_item.pop('downvotes', 0)}
            final_items.append(post_item)

            # Find and append related comments
            related_comments = comments_df[comments_df['post_id'] == post_item['id']]
            for _, comment_row in related_comments.iterrows():
                comment_item = comment_row.to_dict()
                comment_item.pop('title', None)
                comment_item['engagements'] = {'upvotes': comment_item.pop('upvotes', 0), 'downvotes': comment_item.pop('downvotes', 0)}
                final_items.append(comment_item)

        static_json['items'] = final_items

    if platform.upper() == 'TWITTER':
        df = pd.read_json(os.path.join(script_dir,'twitter_data/processed/filtered_jan_2023.json'))

        # We will sample from our dataset and establish an empty parent_id column
        sample = df.sample(n=x, random_state=seed_no).reset_index(drop=True)
        sample['parent_id'] = [None] * len(sample)

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
        for _, row in sample.iterrows():
            transformed_row = {
                "id": row['id'],
                "parent_id": row.get('parent_id', ''),
                "text": row['text'],
                "author_name_hash": row['author_id'],
                "type": "tweet",
                "created_at": row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['created_at']) else '',
                "engagements": {
                    'reply': row.get('reply_count', 0),
                    'repost': row.get('retweet_count', 0),
                    'like': row.get('like_count', 0),
                    'quote': row.get('quote_count', 0)
                }
            }
            transformed_data.append(transformed_row)

        static_json["items"] = transformed_data

    with open(os.path.join(os.path.dirname(__file__), f'final_{platform}_data.json'), 'w', encoding='utf-8') as file:
        json.dump(static_json, file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample data from platforms')
    parser.add_argument('-p', '--platform', type=str, help='Platform to pull data from')
    args = parser.parse_args()
    platform = args.platform

    data_puller(platform)
