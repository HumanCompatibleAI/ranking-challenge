import requests
import time

# Sample data containing multiple text items
data = {
    "session": {
        "user_id": "193a9e01-8849-4e1f-a42a-a859fa7f2ad3",
        "user_name_hash": "6511c5688bbb87798128695a283411a26da532df06e6e931a53416e379ddda0e",
        "current_time": "2024-01-20 18:41:20",
    },
    "items": [
        {
            "id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "title": "this is the post title, available only on reddit",
            "text": "this is the worst thing I have ever seen!",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "post",
            "platform": "reddit",
            "created_at": "2023-12-06 17:02:11",
            "enagements": {
                "upvote": 34,
                "downvote": 27
            }
        },
        {
            "id": "a4c08177-8db2-4507-acc1-1298220be98d",
            "text": "this thing is ok.",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "comment",
            "platform": "reddit",
            "created_at": "2023-12-08 11:32:12",
            "enagements": {
                "upvote": 3,
                "downvote": 5
            }
        }, 
        {
            "id": "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
            "text": "this is amazing!",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "comment",
            "platform": "reddit",
            "created_at": "2023-12-08 11:32:12",
            "enagements": {
                "upvote": 3,
                "downvote": 5
            }
        }

    ]
}

# Wait for the Flask app to start up
time.sleep(2)

# Send POST request to the API
response = requests.post("http://localhost:5001/analyze_sentiment", json=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    try:
        # Attempt to parse the JSON response
        json_response = response.json()
        print(json_response)
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response. Response may be empty.")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)