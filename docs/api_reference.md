# Prosocial Ranking Challenge API reference

## Endpoint

Your ranker should be implemented as a service that accepts an HTTP POST request at `/rank`. The request and response are JSON.

## Request/response format

Your ranker should accept a list of social media posts and comments, each with a corresponding ID, in JSON format:

### Request

(this example is a single post with two threaded comments)

```jsonc
{
  "session": {
    "user_id": "1cfe49e5-02b6-4e58-a376-4b254a62650e",
    "user_name_hash": "0af8c7486e97a23b4631283970f55a3c51338cbf7a7748ca39449a895822be84",
    "platform": "reddit",
    "current_time": "2024-04-09T19:29:38.072017Z"
  },
  "items": [
    {
      "id": "fde9c535-2d98-45db-b2d9-c3f8c4de0330",
      "post_id": null,
      "parent_id": null,
      "title": null,
      "text": "Sed error repellat minima ex. Numquam recusandae unde perspiciatis quasi suscipit. Natus repellat voluptate nostrum vel.",
      "author_name_hash": "2e7a2066f0d892ecfd656fa64c1081aa9c6778fb0d22217240a62377435c9ace",
      "type": "post",
      "created_at": "2024-04-09T19:29:38.071245Z",
      "engagements": {
        "upvote": 16,
        "downvote": 38,
        "comment": 46,
        "award": 4
      }
    },
    {
      "id": "1d4d65c1-32bc-486b-bb44-761f33820f12",
      "post_id": "fde9c535-2d98-45db-b2d9-c3f8c4de0330",
      "parent_id": null,
      "title": null,
      "text": "Incidunt temporibus at maiores ratione eveniet facere. Eligendi nulla ipsa. Temporibus ex magnam voluptate enim laborum quod.",
      "author_name_hash": "e601eae141746a9677174503e03ee41298f8b1e89ba63565edf4ed0553fdd40a",
      "type": "comment",
      "created_at": "2024-04-09T19:29:38.071843Z",
      "engagements": {
        "upvote": 38,
        "downvote": 2,
        "comment": 9,
        "award": 11
      }
    },
    {
      "id": "ceb75c43-a4f6-4426-a7af-5b178a6fc19a",
      "post_id": "fde9c535-2d98-45db-b2d9-c3f8c4de0330",
      "parent_id": "1d4d65c1-32bc-486b-bb44-761f33820f12",
      "title": null,
      "text": "Nemo suscipit consequuntur officia blanditiis repellendus dolor neque. Dolore reiciendis adipisci reprehenderit blanditiis ad iste hic.",
      "author_name_hash": "911fb438baa1eb6bbb28b4af3419150fbc44409f5129c400ef4ab58c02102a6b",
      "type": "comment",
      "created_at": "2024-04-09T19:29:38.071940Z",
      "engagements": {
        "upvote": 18,
        "downvote": 0,
        "comment": 29,
        "award": 36
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
    "fde9c535-2d98-45db-b2d9-c3f8c4de0330",
    "1d4d65c1-32bc-486b-bb44-761f33820f12",
    "c9c0ea77-7501-4b34-b1a3-f56e41a14f44",
    "10f32cf7-4566-41f9-b07b-6655f4f7fe46"
  ],
  "new_items": [
    {
      "id": "c9c0ea77-7501-4b34-b1a3-f56e41a14f44",
      "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert"
    },
    {
      "id": "10f32cf7-4566-41f9-b07b-6655f4f7fe46",
      "url": "https://reddit.com/r/PRCExample/comments/1f33ead/another_example"
    }
  ]
}
```

You do not need to return the same number of content items as you received. However, keep in mind that making a significant change in the number of items could have a negative impact on the user experience.

## Pydantic models

We have a set of pydanitc models, which are the source of truth for the API format. Using them, you can encode, parse, and validate the request and response json. You can also use them natively in fastapi. The examples above were generated from these models.

You can always find the most current version in [examples/models](https://github.com/HumanCompatibleAI/ranking-challenge/tree/main/examples/models)

## Request fields

### Session fields

- `user_id`: A unique ID for this study participant.
- `user_name_hash`: A (salted) hash of the user's username. We'll do our best to make it match the `author_name_hash` on posts authored by the current user.
- `platform`: One of `reddit`, `twitter`, `facebook`
- `current_time`: The current time according to the user's browser, in UTC, in `YYYY-MM-DD hh:mm:ss` format.

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
