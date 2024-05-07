import hashlib
import time
from random import randint
from uuid import uuid4

from faker import Faker

fake = Faker(locale="la")  # remove locale to get rid of the fake latin

from ranking_challenge.request import ContentItem, RankingRequest, Session
from ranking_challenge.response import RankingResponse
from ranking_challenge.survey import SurveyResponse


def fake_request(n_posts=1, n_comments=0, platform="reddit"):
    posts = [fake_item(platform=platform, type="post") for _ in range(n_posts)]
    comments = []
    for post in posts:
        last_comment_id = None
        for _ in range(n_comments):
            comments.append(
                fake_item(
                    platform=platform,
                    type="comment",
                    post_id=post.id,
                    parent_id=last_comment_id,
                )
            )
            last_comment_id = comments[-1].id

    return RankingRequest(
        session=Session(
            user_id=str(uuid4()),
            user_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
            cohort="AB",
            platform=platform,
            current_time=time.time(),
        ),
        survey=SurveyResponse(
            party_id="democrat",
            support="strong",
            party_lean="democrat",
            sex="female",
            age=3,
            education=4,
            ideology=5,
            income=6,
            ethnicity="native_american",
            socmed_use=7,
            browser_perc=0.8,
            mobile_perc=0.2,
        ),
        items=posts + comments,
    )


def fake_item(platform="reddit", type="post", post_id=None, parent_id=None):
    if platform == "reddit":
        engagements = {
            "upvote": randint(0, 50),
            "downvote": randint(0, 50),
            "comment": randint(0, 50),
            "award": randint(0, 50),
        }
    elif platform == "twitter":
        engagements = {
            "like": randint(0, 50),
            "retweet": randint(0, 50),
            "comment": randint(0, 50),
            "share": randint(0, 50),
        }
    elif platform == "facebook":
        engagements = {
            "like": randint(0, 50),
            "love": randint(0, 50),
            "care": randint(0, 50),
            "haha": randint(0, 50),
            "wow": randint(0, 50),
            "sad": randint(0, 50),
            "angry": randint(0, 50),
            "comment": randint(0, 50),
            "share": randint(0, 50),
        }
    else:
        raise ValueError(f"Unknown platform: {platform}")

    return ContentItem(
        id=str(uuid4()),
        text=fake.text(),
        post_id=post_id,
        parent_id=parent_id,
        author_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
        type=type,
        created_at=time.time(),
        embedded_urls=[fake.url() for _ in range(randint(0, 3))],
        engagements=engagements,
    )


def fake_response(ids, n_new_items=1):
    new_items = [fake_new_item() for _ in range(n_new_items)]

    ids = list(ids) + [item["id"] for item in new_items]

    return RankingResponse(ranked_ids=ids, new_items=new_items)


def fake_new_item():
    return {
        "id": str(uuid4()),
        "url": fake.url(),
    }

# if run from command line
def main():
    request = fake_request(n_posts=1, n_comments=2)
    print("Request:")
    print(request.model_dump_json(indent=2))

    # use ids from request
    response = fake_response([item.id for item in request.items], 2)
    print("\nResponse:")
    print(response.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
