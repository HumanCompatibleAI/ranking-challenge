# Importing of relevant packages
import numpy as np
import random
import pandas as pd
from pathlib import Path
import os
import hashlib
from datetime import datetime
import json

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
    
    
    '''
    if platform.upper() not in (name.upper() for name in platforms):
        print("Not an applicable platform. Try again")
        
    x = int(input("Please input how many data points you wish to sample (suggested: 500):"))
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
        df = pd.read_csv(os.path.join(script_dir,'Facebook Data/Processed/filtered_comment_post.csv'))
        
        sample = df.sample(n=x, random_state=seed_no)
        sample = sample.to_dict(orient='records')
        
        for item in sample:
            item['engagements'] = {
                'likes': item.pop('like'),
                'love': item.pop('love'),
                'haha': item.pop('haha'),
                'wow': item.pop('wow'),
                'sad': item.pop('sad'),
                'angry': item.pop('angry'),
                'comment': None,
                'shares': item.pop('shares') 
            }
            # Adjust for optional fields
            if item['parent_id'] == '':
                item.pop('parent_id')
            if item['post_id'] == '':
                item.pop('post_id')
                
        static_json['items'] = sample
        # final_json_string = json.dumps(static_json, indent=4) -> Maybe
        
    if platform.upper() == 'REDDIT':
        df = pd.read_csv(os.path.join(script_dir,'Reddit Data/Processed/filtered_may_2015.csv'))
            
        sample = df.sample(n=x, random_state=seed_no)
        sample = sample.to_dict(orient='records')
        
        for item in sample:
            item['engagements'] = {
                'score': item.pop('score')
                # 'downvote': item.pop('downvotes') 
            }
            # Adjust for optional fields
            if item['parent_id'] == '':
                item.pop('parent_id')
            if item['post_id'] == '':
                item.pop('post_id')
        
        static_json['items'] = sample
        # final_json_string = json.dumps(static_json, indent=4) -> Maybe
        
    if platform.upper() == 'TWITTER': 
        df = pd.read_json(os.path.join(script_dir,'Twitter Data/Processed/filtered_jan_2023.json'))
        
        sample = df.sample(n=x, random_state=seed_no)
        
        transformed_data = []
        
        for _, row in sample.iterrows():
            transformed_row = {
                "id": row['id'], 
                "text": row['text'],
                "author_name_hash": row['author_id'],
                "type": "tweet",
                "created_at": row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['created_at']) else '',
                "engagements": {
                    'reply': row.get('reply_count'),
                    'repost': row.get('retweet_count'),
                    'like': row.get('like_count'),
                    'quote': row.get('quote_count')
                }
            }
            transformed_data.append(transformed_row)
            
            static_json["items"] = transformed_data
    
    
    with open(os.path.join(os.path.dirname(__file__), f'final_{platform}_data.json'), 'w', encoding='utf-8') as file:
        json.dump(static_json, file, indent=4)


# data_puller('facebook')
# data_puller('reddit')
# data_puller('twitter')

    
    
    
    
    


