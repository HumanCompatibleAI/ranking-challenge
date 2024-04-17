# Sample data containing multiple text items

CHATGPT_EXAMPLE = {
    "session": {
        "user_id": "193a9e01-8849-4e1f-a42a-a859fa7f2ad3",
        "user_name_hash": "6511c5688bbb87798128695a283411a26da532df06e6e931a53416e379ddda0e",
        "platform": "reddit",
        "cohort": "AB",
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
            "embedded_urls": [],
            "engagements": {"upvote": 34, "downvote": 27, "comment": 20, "award": 0},
        },
        {
            "id": "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
            "post_id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "parent_id": "",
            "text": "this is amazing!",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "comment",
            "platform": "reddit",
            "created_at": "2023-12-08 11:32:12",
            "embedded_urls": [],
            "engagements": {"upvote": 15, "downvote": 2, "comment": 22, "award": 2},
        },
        {
            "id": "a4c08177-8db2-4507-acc1-1298220be98d",
            "post_id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "parent_id": "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
            "text": "this thing is ok.",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "comment",
            "platform": "reddit",
            "created_at": "2023-12-08 11:35:00",
            "embedded_urls": [],
            "engagements": {"upvote": 3, "downvote": 5, "comment": 10, "award": 0},
        },
    ],
}

# some new posts that can be added to the response
NEW_POSTS = [
    {
        "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
        "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
    },
    {
        "id": "1fcbb164-f81f-4532-b068-2561941d0f63",
        "url": "https://reddit.com/r/PRCExample/comments/ef56a23/another_example_to_insert",
    },
]
