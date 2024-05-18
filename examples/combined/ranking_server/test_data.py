# Sample data containing multiple text items

BASIC_EXAMPLE = {
    "session": {
        "session_id": "719f30a1-03bb-4d41-a654-138da5c43547",
        "user_id": "193a9e01-8849-4e1f-a42a-a859fa7f2ad3",
        "user_name_hash": "6511c5688bbb87798128695a283411a26da532df06e6e931a53416e379ddda0e",
        "platform": "reddit",
        "cohort": "AB",
        "url": "https://reddit.com/r/PRCExample/1f4deg/example_to_insert",
        "current_time": "2024-01-20 18:41:20",
    },
    "items": [
        {
            "id": "should-rank-high",
            "title": "this is the post title, available only on reddit",
            "text": "this is the worst thing I have ever seen!",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "embedded_urls": [],
            "type": "post",
            "created_at": "2023-12-06 17:02:11",
            "engagements": {"upvote": 34, "downvote": 27, "comment": 20, "award": 0},
        },
        {
            "id": "should-rank-low",
            "post_id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "parent_id": "",
            "text": "this is amazing! foo!",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "embedded_urls": [],
            "type": "comment",
            "created_at": "2023-12-08 11:32:12",
            "engagements": {"upvote": 15, "downvote": 2, "comment": 22, "award": 2},
        },
        {
            "id": "should-rank-high-2",
            "post_id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "parent_id": "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
            "text": "this thing is ok.",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "embedded_urls": [],
            "type": "comment",
            "created_at": "2023-12-08 11:35:00",
            "engagements": {"upvote": 3, "downvote": 5, "comment": 10, "award": 0},
        },
    ],
}

# some new posts that can be added to the response
NEW_POSTS = {
    "facebook": [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://www.facebook.com/photo/?fbid=10160163058503437&set=a.10156555775028437",
        },
        {
            "id": "1fcbb164-f81f-4532-b068-2561941d0f63",
            "url": "https://www.facebook.com/photo/?fbid=10160163060778437&set=a.10156555775028437",
        },
    ],
    "reddit": [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://www.reddit.com/r/bestOfReddit/comments/hb55wg/rick_astley_gets_rick_rolled/",
        },
        {
            "id": "1fcbb164-f81f-4532-b068-2561941d0f63",
            "url": "https://www.reddit.com/r/maru/comments/13co2hm/liquid_maru_with_level_10_of_meltability/",
        },
    ],
    "twitter": [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://twitter.com/Horse_ebooks/status/218439593240956928",
        },
        {
            "id": "1fcbb164-f81f-4532-b068-2561941d0f63",
            "url": "https://twitter.com/elonmusk/status/1519480761749016577",
        },
    ],
}
