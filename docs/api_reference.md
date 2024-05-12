# Prosocial Ranking Challenge API reference

## Endpoint

Your ranker should be implemented as a service that accepts an HTTP POST request at `/rank`. The request and response are JSON.

## Request/response format

Your ranker should accept a list of social media posts and comments, each with a corresponding ID, in JSON format.

### Request

(this example is a single post with two threaded comments)

```jsonc
Request:
{
  "session": {
    "user_id": "74f2e773-5bcd-4936-8d21-dbd34d4f8b18",
    "user_name_hash": "a7a80e8ea489379a64f8d188fceefa6c77550f1682ee2b76b09d5270a7378cc1",
    "cohort": "AB",
    "platform": "reddit",
    "current_time": "2024-04-15T23:59:46.295928Z"
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
      "id": "76d8710b-e1d2-40b6-8d99-084d4bc7f3ce",
      "post_id": null,
      "parent_id": null,
      "title": null,
      "text": "Atque tempore unde.\nSint quia minima blanditiis. Rem veritatis soluta quidem excepturi quam suscipit. Sequi doloribus consequuntur error nulla tenetur.",
      "author_name_hash": "d9f7b073fc3a7c142d154f4edcce9837ba3c35c855281942b08f19340b4439a8",
      "type": "post",
      "embedded_urls": [
        "https://dominguez.com/",
        "https://everett-gordon.biz/",
        "https://www.smith-miles.com/"
      ],
      "created_at": "2024-04-15T23:59:46.291735Z",
      "engagements": {
        "upvote": 28,
        "downvote": 15,
        "comment": 12,
        "award": 16
      }
    },
    {
      "id": "620c78e8-5e15-4f82-a008-63cccf4cfdc2",
      "post_id": "76d8710b-e1d2-40b6-8d99-084d4bc7f3ce",
      "parent_id": null,
      "title": null,
      "text": "Necessitatibus ullam ullam est consequuntur. Eligendi dolorem officiis eligendi harum.",
      "author_name_hash": "da41ff70b25c5ea3ebb595e9dd595688a7c5204fd3b89c5cb9005633799e493e",
      "type": "comment",
      "embedded_urls": [
        "https://www.fox.com/"
      ],
      "created_at": "2024-04-15T23:59:46.295685Z",
      "engagements": {
        "upvote": 13,
        "downvote": 50,
        "comment": 50,
        "award": 35
      }
    },
    {
      "id": "ae2ca8be-7faf-4d6e-95dd-2e5f1c27961e",
      "post_id": "76d8710b-e1d2-40b6-8d99-084d4bc7f3ce",
      "parent_id": "620c78e8-5e15-4f82-a008-63cccf4cfdc2",
      "title": null,
      "text": "Repellat sit sed animi sunt. Sapiente quam temporibus itaque tenetur dolores excepturi. Harum ullam magnam dolores vel fuga aut.",
      "author_name_hash": "c54177a4d5fc74be8efc20af12c3c069adb646e7db712a347f05f12b056e732c",
      "type": "comment",
      "embedded_urls": [],
      "created_at": "2024-04-15T23:59:46.295851Z",
      "engagements": {
        "upvote": 19,
        "downvote": 31,
        "comment": 32,
        "award": 40
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
    "76d8710b-e1d2-40b6-8d99-084d4bc7f3ce",
    "620c78e8-5e15-4f82-a008-63cccf4cfdc2",
    "ae2ca8be-7faf-4d6e-95dd-2e5f1c27961e",
    "5e5a9aca-ce2d-4026-8386-e5d023d770a4",
    "d285ae38-463d-4065-9478-a41a86710e97"
  ],
  "new_items": [
    {
      "id": "5e5a9aca-ce2d-4026-8386-e5d023d770a4",
      "url": "https://williams-weber.com/"
    },
    {
      "id": "d285ae38-463d-4065-9478-a41a86710e97",
      "url": "https://grant-kent.org/"
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
- `cohort`: The cohort to which the user has been assigned. You can safely ignore this. It is used by the PRC request router.
- `platform`: One of `reddit`, `twitter`, `facebook`
- `current_time`: The current time according to the user's browser, in UTC, in `YYYY-MM-DD hh:mm:ss` format.

### Survey fields

Demographic information about the user from the PRC intake survey. More documentation on the format is available in `examples/models/survey.py`

### Content items

- `id`: A unique ID describing a specific piece of content. We will do our best to make an ID for a given item persist between requests, but that property is not guaranteed.
- `parent_id`: For threaded comments, this identifies the comment to which this one is a reply. Blank for top-level comments.
- `post_id`: The ID of the post to which this comment belongs. Useful for linking comments to their post when comments are shown in a feed. Currently this only happens on Facebook.
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
