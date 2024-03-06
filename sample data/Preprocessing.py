
import os
import sqlite3
import pandas as pd
import hashlib
import json
from datetime import datetime


# Hashing function to anonymise certain data points 

def hashed(x):
    '''
    This function will hash the respective arg using SHA-256.
    
    It converts x into a string, then applies a SHA-256 Hash object to it
    
    '''
    if pd.isna(x):
        return None  
    added_salt = os.urandom(16)
    stringed = str(x).encode() + added_salt
    hash_object = hashlib.sha256()
    hash_object.update(stringed)
    return hash_object.hexdigest()

# REDDIT PREPROCESSING

# This will get the directory in our git
reddit_relative_path = 'Reddit Data/Raw/reddit_may_2015.csv'
script_dir = os.path.dirname(__file__) 
reddit_file_path = os.path.join(script_dir, reddit_relative_path)
reddit_data= pd.read_csv(reddit_file_path,low_memory=False).reset_index()

# We then rename columns and hash the columns that require anonymity
reddit_data['type'] = "Comment"
reddit_data.rename(columns={'ups':'upvotes', 'created_utc':'created_at', 'link_id':'post_id', 'downs':'downvotes', 'body':'text', 'author': 'author_name_hash'}, inplace=True)

reddit_data['created_at'] = pd.to_numeric(reddit_data['created_at'], errors='coerce') # Some columns are errors
reddit_data = reddit_data.dropna(subset=['created_at'])
reddit_data['created_at'] = pd.to_datetime(reddit_data['created_at'], unit='s')
reddit_data['created_at'] = reddit_data['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

for item in reddit_data['created_at']:
    item = str(item)
    

hash_col = ['index', 'post_id', 'parent_id', 'author_name_hash']
for col in hash_col:
    reddit_data[col] = reddit_data[col].apply(hashed)

# Lastly, we select relevant columns and then export to a csv within the 'Processed' folder
filtered_reddit = reddit_data[['index', 'parent_id', 'post_id', 'text', 'author_name_hash', 'type', 'created_at', 'score']] # upvotes', 'downvotes' removed because of incorrect info
filtered_reddit.to_csv(os.path.join(script_dir,'Reddit Data/Processed/filtered_may_2015.csv'), index=False)


# FACEBOOK PREPROCESSING

# This will get the directory in our git
fb_comment_relative_path = 'Facebook Data/Raw/FB_news_comments.csv'
fb_post_relative_path = 'Facebook Data/Raw/FB_news_posts.csv'
script_dir = os.path.dirname(__file__) 
comment_file_path = os.path.join(script_dir, fb_comment_relative_path)
post_file_path = os.path.join(script_dir, fb_post_relative_path)
comments = pd.read_csv(comment_file_path)
posts = pd.read_csv(post_file_path)

comments['type'] = "Comment"
posts['type'] = 'Post'
comments[['from_id', 'c_post_id']] = comments['post_name'].str.split('_', expand=True)
posts[['p_post_id', 'post_name']] = posts['post_id'].str.split('_', expand=True)

merged = pd.concat([posts, comments], axis=0)

# To create author_ids, we will need to use from_id for comments and page_id from posts
merged['author_name_hash'] = merged['page_id'].combine_first(merged['from_id'])
merged['all_post_ids'] = merged['p_post_id'].combine_first(merged['c_post_id'])
merged['parent_id'] = None

# For posts, we need to count the number of comments. There are a number of duplicate rows we must also drop first.
merged = merged.drop_duplicates()
# comments_count = merged[merged['type'] == 'Comment']['c_post_id'].value_counts().reset_index()

# merged = pd.merge(merged, comments_count, on='all_post_ids', how='left')

# We then rename columns and apply hashing function
merged = merged.drop(columns = ['post_id']).reset_index()
merged.rename(columns={'react_haha':'haha', 'react_like':'like', 'react_angry':'angry', 'react_love':'love',
                       'react_sad':'sad', 'react_wow':'wow', 'created_time':'created_at'
                       , 'message':'text', 'c_post_id':'post_id', 'index':'id', 'comments_count':'comments'}, inplace=True)

# Lastly we replace NaN values with 0
columns = ['like', 'love', 'haha', 'wow', 'sad', 'angry', 'shares']
merged.loc[:, columns] = merged[columns].fillna(0)

merged['created_at_temp'] = pd.to_datetime(merged['created_at'], errors='coerce') # we need to remove erroneous values 
merged = merged[~pd.isna(merged['created_at_temp'])]
merged['created_at'] = pd.to_datetime(merged['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

for item in merged['created_at']:
    item = str(item)
    
hash_col = ['id', 'post_id', 'author_name_hash']
for col in hash_col:
    merged[col] = merged[col].apply(hashed)

filtered_facebook = merged[['id','parent_id','post_id','text','author_name_hash','type','created_at','like', 'love', 'haha', 'wow', 'sad', 'angry', 'shares']]
filtered_facebook.to_csv(os.path.join(script_dir,'Facebook Data/Processed/filtered_comment_post.csv'), index=False)

# TWITTER PREPROCESSING
script_dir = os.path.dirname(__file__) 

files = ['samp1', 'samp2', 'samp3', 'samp4', 'samp5']
jsons= []

for file_name in files:
    file_path = os.path.join(script_dir, f'Twitter Data/Raw/{file_name}.json')
    with open(file_path, 'r', encoding='utf-8') as json_file:
        for line in json_file:
            json_obj = json.loads(line.strip())
            # Extract 'data' part and apply hashing where needed
            if 'data' in json_obj:
                data_part = json_obj['data']
                # Hash specific fields, e.g., 'id' and 'author_id'
                if 'id' in data_part:
                    data_part['id'] = hashed(data_part['id'])
                if 'author_id' in data_part:
                    data_part['author_id'] = hashed(data_part['author_id'])
                if 'created_at' in data_part:
                    created = datetime.strptime(data_part['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    data_part['created_at'] = str(created.strftime('%Y-%m-%d %H:%M:%S'))
                jsons.append(data_part)

with open(os.path.join(script_dir,'Twitter Data/Processed/filtered_jan_2023.json'), 'w', encoding='utf-8') as output_file:
    json.dump(jsons, output_file, indent=4)
    
    
# database_path = '/u/j/d/database2.sqlite'
# conn = sqlite3.connect(database_path)
# query = "SELECT downs FROM May2015 LIMIT 2000000"
# df = pd.read_sql_query(query, conn)
# conn.close()
# df.to_csv('/Users/jamesclark/Downloads/reddit_downs.csv', index=False)
