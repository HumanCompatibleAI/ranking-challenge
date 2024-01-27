# Prosocial Ranking Challenge API reference

## Endpoint

Your ranker should be implemented as a service that accepts an HTTP POST request at `/rank`. The request and response are JSON.

## Request/response format

_NOTE: This is provisional, and will almost certainly change._

Your ranker should accept a list of social media posts and comments, each with a corresponding ID, in JSON format:

```json
{
    "session": {
        "user_id": "193a9e01-8849-4e1f-a42a-a859fa7f2ad3",
        "user_name_hash": "6511c5688bbb87798128695a283411a26da532df06e6e931a53416e379ddda0e",
        "platform": "reddit",
        "current_time": "2024-01-20 18:41:20",
    },
    "items": [
        {
            "id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "title": "this is the post title, available only on reddit",
            "text": "this is a social media post",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "post",
            "created_at": "2023-12-06 17:02:11",
            "enagements": {
                "upvote": 34,
                "downvote": 27
            }
        },
        {
            "id": "a4c08177-8db2-4507-acc1-1298220be98d",
            "text": "this is a comment, by the author of the post",
            "author_name_hash": "60b46b7370f80735a06b7aa8c4eb6bd588440816b086d5ef7355cf202a118305",
            "type": "comment",
            "created_at": "2023-12-08 11:32:12",
            "enagements": {
                "upvote": 3,
                "downvote": 5
            }
        }
    ]
}
```

Your ranker should return an ordered list of IDs. You can also remove items by removing an ID, or add items by inserting a new ID that you generate. For new posts (only posts insertion is supported), also provide the post URL.

```json
{
    "ranked_ids": [
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
        "571775f3-2564-4cf5-b01c-f4cb6bab461b"
    ],
    "new_items": [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
        }
    ]
}
```

You do not need to return the same number of content items as you received. However, keep in mind that making a significant change in the number of items could have a negative impact on the user experience.

## Request fields

### Session fields

- `user_id`: A unique ID for this study participant.
- `user_name_hash`: A (salted) hash of the user's username. We'll do our best to make it match the `author_name_hash` on posts authored by the current user.
- `platform`: One of `reddit`, `twitter`, `facebook`
- `current_time`: The current time according to the user's browser, in UTC, in `YYYY-MM-DD hh:mm:ss` format.

### Content items

- `id`: A unique ID describing a specific piece of content. We will do our best to make an ID for a given item persist between requests, but that property is not guaranteed.
- `text`: The text of the content item. Assume UTF-8, and that leading and trailing whitespace have been trimmed.
- `author_name_hash`: A hash of the author's name (salted). Use this to determine which posts are by the same author. When the post is by the current user, this should match `user_name_hash`.
- `type`: Whether the content item is a `post` or `comment`
- `created_at`: The time that the item was created in UTC, in `YYYY-MM-DD hh:mm:ss` format, at the highest resolution available (which may be as low as the hour).

#### Engagements

Integer counts of engagements

- Reddit, `upvote, downvote`.
- X (Twitter): `reply, repost, like, view`
- Facebook: `like, love, care, haha, wow, sad, angry, comment, share`

#### Content types (the `type` field)

- Reddit and Facebook: `post, comment`
- X (Twitter): `post`

### Platform-specific fields

Some fields are only available for a subset of platforms and content types:

`title` is only available on Reddit posts (not comments)

## Response fields

- `ranked_ids`: A list of the content item IDs, in the order in which you would like them to be ranked.
- `new_items`: A list of new content items to insert into the results.

### Inserting new content items

To add an item, the item must be public (or accessible to the current user). The extension will fetch the item and insert it into the user's feed. This limitation exists for a few reasons:

1. For the content item to function, there must be a representation of it on the platform. We can't just make a new fake item because all the links and buttons on it would not work.
2. We rely on the platform's access controls to guarantee that the user is allowed to see the content.

If you have specific items you would like to insert as part of the experiment, you can create public posts with those items.

Fields

- `id`: A unique ID for this post. This can be a platform-generated ID, or you can generate it. It just needs to be unique.
- `url`: The full URL for the content item.

At present, we expect content item insertion to only work for posts. If you need to be able to insert comments as well, talk to us.

## HTTP response codes

In general, our caller will log any non-success response code. Returning a correct code and error may help with debugging. Some codes you could consider returning:

- `200`: Success. Everything worked and the response should be considered valid
- `400`: Bad request. You validated or attempted to parse the input and it failed.a
- `413`: Request too long. You have a limit to the amount of data you can receive and it was exceeded.
- `429`: Too many requests. There is a rate-limit (potentially upstream) that was exceeded.
- `500`: Internal Server Error. Something failed in your application.
- `503`: Service Unavailable. Your service isn't ready to handle requests. Often returned during startup.

The caller will not follow redirects.

For the initial submission you may use an external service. If you receive an error from that service, you can also forward it along with its response code.
