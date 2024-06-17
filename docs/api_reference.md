# Prosocial Ranking Challenge API reference

## Endpoint

Your ranker should be implemented as a service that accepts an HTTP POST request at `/rank`. The request and response are JSON.

## Request/response format

Your ranker should accept a list of social media posts and comments, each with a corresponding ID, in JSON format.

### Request

(this example is a single post with two threaded comments, please note that upvote and downvote are now deprecated fields)

```jsonc
Request:
{
  "session": {
    "session_id": "fd5d9298-4ca8-4d73-969a-e8da20ff321b",
    "user_id": "41d01393-090a-4fcb-942b-28d87a7a06f3",
    "user_name_hash": "62a7c41518817a23706dfd600f29b1329eee18c69b014ae34265d7cf0ed183f1",
    "cohort": "AB",
    "cohort_index": "1000",
    "platform": "reddit",
    "url": "https://reddit.com/r/technology",
    "current_time": "2024-05-13T21:08:32.211000Z"
  },
  "survey": {
    "party_id": "democrat",
    "party_write_in": null,
    "support": "strong",
    "party_lean": "democrat",
    "sex": "female",
    "age": 3,
    "education": 4,
    "ideology": 5,
    "income": 6,
    "ethnicity": "native_american",
    "ethnicity_write_in": null,
    "socmed_use": 7,
    "browser_perc": 0.8,
    "mobile_perc": 0.2
  },
  "items": [
    {
      "id": "368ba07d-a25f-49b1-a9dc-c1e909defe38",
      "original_rank": 5,
      "post_id": null,
      "parent_id": null,
      "title": null,
      "text": "Perspiciatis itaque ea praesentium assumenda recusandae doloremque. Esse cupiditate praesentium praesentium minima. Quam odio vitae consequatur occaecati modi.",
      "author_name_hash": "0d231f75b907c4106f2d4d72437b55f9527babb045ac07ca791871c902d556f4",
      "type": "post",
      "embedded_urls": [],
      "created_at": "2024-05-13T21:08:32.210288Z",
      "engagements": {
        "upvote": 4,
        "downvote": 6,
        "score": -2,
        "comment": 12,
        "award": 4
      }
    },
    {
      "id": "8421a4c8-f21b-482f-a8f4-ff1489365470",
      "original_rank": 204,
      "post_id": "368ba07d-a25f-49b1-a9dc-c1e909defe38",
      "parent_id": null,
      "title": null,
      "text": "Itaque suscipit fuga consectetur sint totam reiciendis. Praesentium corrupti quasi aperiam molestias similique.",
      "author_name_hash": "778f795ac95b76ce554a685d937bf25082ec51c88bc15c68f7089c38fea40eda",
      "type": "comment",
      "embedded_urls": [
        "https://rodriguez-davis.info/"
      ],
      "created_at": "2024-05-13T21:08:32.210409Z",
      "engagements": {
        "upvote": 27,
        "downvote": 19,
        "score": 8,
        "comment": 21,
        "award": 29
      }
    },
    {
      "id": "10b94628-b443-4b0a-ba9f-2efaafd19bff",
      "original_rank": 77,
      "post_id": "368ba07d-a25f-49b1-a9dc-c1e909defe38",
      "parent_id": "8421a4c8-f21b-482f-a8f4-ff1489365470",
      "title": null,
      "text": "Odio rerum quos nostrum ut sapiente possimus. Expedita fuga dolores quas maiores. Quos repellat deserunt corrupti assumenda amet debitis.",
      "author_name_hash": "c97ea217787cd8d9fc8166c662075382b2ec0e2bc93bb2c82bf68f0b6527f05e",
      "type": "comment",
      "embedded_urls": [
        "https://www.johnson.com/",
        "http://www.mckinney-johnson.com/",
        "https://www.flowers.net/"
      ],
      "created_at": "2024-05-13T21:08:32.210636Z",
      "engagements": {
        "upvote": 34,
        "downvote": 27,
        "score": 7,
        "comment": 5,
        "award": 16
      }
    }
  ]
}
```

### Response

Your ranker should return an ordered list of IDs. You can also remove items by removing an ID, or add items by inserting a new ID that you generate. For new posts (only posts insertion is supported), also provide the post URL.

```jsonc
{
  "ranked_ids": [
    "368ba07d-a25f-49b1-a9dc-c1e909defe38",
    "8421a4c8-f21b-482f-a8f4-ff1489365470",
    "10b94628-b443-4b0a-ba9f-2efaafd19bff",
    "abe08409-3421-4aba-8e5f-648f4276dbf0",
    "3950fd29-45d2-4cb3-8cd0-47869ca98eb3"
  ],
  "new_items": [
    {
      "id": "abe08409-3421-4aba-8e5f-648f4276dbf0",
      "url": "https://smith.com/"
    },
    {
      "id": "3950fd29-45d2-4cb3-8cd0-47869ca98eb3",
      "url": "https://www.martinez.com/"
    }
  ]
}
```

You do not need to return the same number of content items as you received. However, keep in mind that making a significant change in the number of items could have a negative impact on the user experience.

## Pydantic models

We have a set of pydanitc models, which are the source of truth for the API format. Using them, you can encode, parse, and validate the request and response json. You can also use them natively in fastapi. The examples above were generated from these models.

You can always find the most current version in [examples/models](https://github.com/HumanCompatibleAI/ranking-challenge/tree/main/module)

To use them, just `pip install ranking-challenge`, and use them to generate and validate your request/response json: [PyPI: ranking-challenge](https://pypi.org/project/ranking-challenge/).

## Request fields

### Session fields

- `user_id`: A unique ID for this study participant.
- `user_name_hash`: A (salted) hash of the user's username. We'll do our best to make it match the `author_name_hash` on posts authored by the current user.
- `session_id`: A unique ID for this page view, updated on navigation events. Use this to determine if two requests came from the same page.
- `cohort`: The cohort to which the user has been assigned. You can safely ignore this. It is used by the PRC request router.
- 'cohort_index': The index of the cohort. Determines which cohort the post will belong to.
- `platform`: One of `reddit`, `twitter`, `facebook`
- `url`: The URL of the page that the user is viewing, minus the query string portion. This can help you to determine which part of the application the user is in.
- `current_time`: The current time according to the user's browser, in UTC, in `YYYY-MM-DD hh:mm:ss` format.

### Survey fields

Demographic information about the user from the PRC intake survey. More documentation on the format is available in `examples/models/survey.py`

### Content items

- `id`: A unique ID describing a specific piece of content. We will do our best to make an ID for a given item persist between requests, but that property is not guaranteed.
- 'original_ranking': The original ranking of the post for the platform.
- `parent_id`: For threaded comments, this identifies the comment to which this one is a reply. Blank for top-level comments.
- `post_id`: The ID of the post to which this comment belongs. Useful for linking comments to their post when comments are shown in a feed. Currently this only happens on Facebook.
- `text`: The text of the content item. Assume UTF-8, and that leading and trailing whitespace have been trimmed.
- `author_name_hash`: A hash of the author's name (salted). Use this to determine which posts are by the same author. When the post is by the current user, this should match `user_name_hash`.
- `type`: Whether the content item is a `post` or `comment`
- `created_at`: The time that the item was created in UTC, in `YYYY-MM-DD hh:mm:ss` format, at the highest resolution available (which may be as low as the hour).

#### Engagements

Integer counts of engagements

- Reddit, `score', ('upvote', 'downvote' have since been deprecated as they are net values and can be replaced with score)
- X (Twitter): `reply, repost, like, view`
- Facebook: `like, love, care, haha, wow, sad, angry, comment, share`

#### Content types (the `type` field)

- Reddit and Facebook: `post, comment`
- X (Twitter): `post`

### Platform-specific fields

Some fields are only available for a subset of platforms and content types:

`title` is only available on Reddit posts (not comments)

### Comment threading

All platforms display comments in threads. If you would like to construct the reply graph, use the `parent_id` field.

When you return a ranking, comments will be sorted according to that ranking, but without breaking the underlying thread structure. Essentially, we will use your global ranking of comments to sort each level of a thread separately.

If you remove a comment, the browser extension will remove its children as well. This is necessary to preserve the integrity of the user experience.

## Response fields

- `ranked_ids`: A list of the content item IDs, in the order in which you would like them to be ranked.
- `new_items`: A list of new content items to insert into the results.

### Inserting new content items

You don't have to add new content items to the feed, but you can if you like. To add an item, the item must be public (or accessible to the current user). The extension will fetch the item and insert it into the user's feed. This limitation exists for a few reasons:

1. For the content item to function, there must be a representation of it on the platform. We can't just make a new fake item because all the links and buttons on it would not work.
2. We rely on the platform's access controls to guarantee that the user is allowed to see the content.

If you have specific items you would like to insert as part of the experiment, you can create public posts with those items.

Fields

- `id`: A unique ID for this post. This can be a platform-generated ID, or you can generate it. It just needs to be unique, and must not contain PII. A GUID is fine.
- `url`: The full URL for the content item.

At present, we expect content item insertion to only work for posts. If you need to be able to insert comments as well, talk to us.

## HTTP response codes

In general, our caller will log any non-success response code. Returning a correct code and error may help with debugging. Some codes you could consider returning:

- `200`: Success. Everything worked and the response should be considered valid
- `400`: Bad request. You validated or attempted to parse the input and it failed.
- `413`: Request too long. You have a limit to the amount of data you can receive and it was exceeded.
- `429`: Too many requests. There is a rate-limit (potentially upstream) that was exceeded.
- `500`: Internal Server Error. Something failed in your application.
- `503`: Service Unavailable. Your service isn't ready to handle requests. Often returned during startup.

The caller will not follow redirects.

For the initial submission you may use an external service. If you receive an error from that service, you can also forward it along with its response code.
