import csv
import hashlib
import inspect
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime

import httpx
from ranking_challenge.fake import fake_request
from ranking_challenge.request import (ContentItem, FacebookEngagements,
                                       RankingRequest, RedditEngagements,
                                       Session, TwitterEngagements)
from ranking_challenge.response import RankingResponse

parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)

# Note: this magical url fixture is defined in conftest.py

TIMEOUT = 30.0


def test_rank_fake(url):
    # Send POST request to the API
    response = httpx.post(
        url,
        content=fake_request().model_dump_json(),
        headers={"content-type": "application/json"},
        timeout=TIMEOUT,
        follow_redirects=True,
    )

    assert (
        response.status_code == 200
    ), f"Request failed with content: {response.content}"

    result = RankingResponse.model_validate_json(response.content)
    print(result, file=sys.stderr)
    # If we got here without raising an exception, the result was valid.


def test_rank_facebook(url):
    with open("test_data/facebook.csv", encoding="utf-8") as f:
        items = []
        reader = csv.DictReader(f)
        for row in reader:
            embedded_urls = re.findall(
                r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", row["text"]
            )
            engagements_dict = {
                key: int(float(row[key] or 0))
                for key in [
                    "like",
                    "love",
                    "haha",
                    "wow",
                    "sad",
                    "angry",
                    "comment",
                    "share",
                ]
            }
            engagements_dict["care"] = 0  # don't care
            engagements = FacebookEngagements(**engagements_dict)

            try:
                item = ContentItem(
                    id=row["id"],
                    post_id=row["all_post_ids"],
                    parent_id=row["parent_id"],
                    text=row["text"],
                    author_name_hash=row["author_name_hash"],
                    type=row["type"].lower(),
                    created_at=row["created_at"],
                    embedded_urls=embedded_urls,
                    engagements=engagements,
                )
            except Exception:
                # skip invalid lines
                continue

            items.append(item)

    check_response(url, "facebook", items)


def test_rank_reddit(url):
    with open("test_data/reddit.csv", encoding="utf-8") as f:
        items = []
        reader = csv.DictReader(f)
        for row in reader:
            embedded_urls = re.findall(
                r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", row["text"]
            )
            engagements = RedditEngagements(
                upvote=int(float(row["upvotes"])),
                downvote=int(float(row["downvotes"])),
                comment=0,
                award=0,
            )

            try:
                item = ContentItem(
                    id=row["id"],
                    post_id=row["post_id"],
                    parent_id=row["parent_id"],
                    text=row["text"],
                    title=row["title"],
                    author_name_hash=row["author_name_hash"],
                    type=row["type"].lower(),
                    created_at=row["created_at"],
                    embedded_urls=embedded_urls,
                    engagements=engagements,
                )
            except Exception:
                # skip invalid lines
                continue

            items.append(item)

    check_response(url, "reddit", items)


def test_rank_twitter(url):
    with open("test_data/twitter.json") as f:
        rows = json.load(f)
        items = []
        i = 0
        for row in rows:
            if row["lang"] != "en":
                continue

            i += 1
            if i > 100:
                break

            embedded_urls = re.findall(
                r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", row["text"]
            )
            engagements = TwitterEngagements(
                retweet=row["public_metrics"]["retweet_count"],
                like=row["public_metrics"]["like_count"],
                comment=row["public_metrics"]["reply_count"],
                share=0,
            )
            author_name_hash = hashlib.sha256(row["author_id"].encode()).hexdigest()

            try:
                item = ContentItem(
                    id=str(uuid.uuid4()),
                    post_id=row["id"],
                    # omitting parent_id for now
                    text=row["text"],
                    author_name_hash=author_name_hash,
                    type="post",
                    created_at=row["created_at"],
                    embedded_urls=embedded_urls,
                    engagements=engagements,
                )
            except Exception:
                # skip invalid lines
                continue

            items.append(item)

    check_response(url, "twitter", items)


def check_response(url, platform, items):
    request = RankingRequest(
        session=Session(
            user_id="i_am_a_user_id",
            user_name_hash="fake_user_name_hash",
            cohort="AB",
            platform=platform,
            current_time=datetime.now(),
        ),
        items=items,
    )

    start = time.time()
    response = httpx.post(
        url,
        content=request.model_dump_json(),
        headers={"content-type": "application/json"},
        timeout=TIMEOUT,
        follow_redirects=True,
    )
    total_time = time.time() - start
    print(f"Request took {total_time:.2f} seconds")

    assert (
        response.status_code == 200
    ), f"Request failed with content: {response.content}"

    try:
        result = RankingResponse.model_validate_json(response.content)
    except Exception as e:
        print(f"Raw response:\n{response.content}", file=sys.stderr)
        raise e

    print(result, file=sys.stderr)

    supplied_ids = set([item.id for item in items])
    received_ids = set([id for id in result.ranked_ids])
    if result.new_items:
        new_ids = set([item.id for item in result.new_items])
    else:
        new_ids = set()

    print(f"Supplied ids: {len(supplied_ids)}")
    print(f"Received ids: {len(received_ids)}")
    print(f"ids removed from ranking: {len(supplied_ids - received_ids)}")
    print(f"New ids added to ranking: {len(received_ids - supplied_ids)}")
    print(f"New items: {len(new_ids)}")
    print(f"New items not included in ranking: {len(new_ids - received_ids)}")

    assert (len(result.ranked_ids)) > 0  # the ranker didn't remove everything
    assert len(supplied_ids) == len(items)  # ids are unique
    assert (
        len(new_ids - received_ids) == 0
    )  # Check to see if the new items were added to the ranking
