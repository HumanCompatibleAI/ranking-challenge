import hashlib
import time
from random import randint
from uuid import uuid4

from faker import Faker
from ranking_challenge.request import ContentItem, RankingRequest, Session
from ranking_challenge.response import RankingResponse
from ranking_challenge.survey import SurveyResponse

fake = Faker(locale="la")  # remove locale to get rid of the fake latin

URI_PATHS = {
    "reddit": ["", "r/aww", "r/politics", "r/programming", "r/technology"],
    "twitter": ["", "jack", "TiredActor", "horse_ebooks"],
    "facebook": ["", "photo", "groups"],
}

platform = "twitter"


def fake_request(n_posts=1, n_comments=0, platform=platform):
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
            session_id=str(uuid4()),
            url=f"https://{platform}.com/{fake.random_element(URI_PATHS[platform])}",
            user_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
            cohort="AB",
            cohort_index=randint(0, 4095),
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
            feed_lean=3,
            socmed_censorship="not_at_all_likely",
            socmed_trust="strongly_distrust",
            percieved_racism="Not_a_problem",
            trump="strongly_unfavorable",
            economic="extremely_negative",
            msm_trust="strongly_distrust",
            immigration="greatly_decreased",
            israel_palestine="strongly_oppose",
            abortion="strongly_oppose",
            climate_change="not_concerned",
            military="strongly_unfavorable",
            political_complexity="never",
            political_understanding="extremely_well",
            political_focus="never",
            voting_likelihood="will_not_vote",
        ),
        items=posts + comments,
    )


def fake_item(platform="reddit", type="post", post_id=None, parent_id=None):
    if platform == "reddit":
        score = randint(-50, 50)
        if score > 0:
            upvote = score
            downvote = 0
        else:
            upvote = 0
            downvote = -score

        engagements = {
            "upvote": upvote,
            "downvote": downvote,
            "score": score,
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

    item = ContentItem(
        id=str(uuid4()),
        original_rank=randint(0, 100),
        text=fake.text(),
        post_id=post_id,
        parent_id=parent_id,
        author_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
        type=type,
        created_at=time.time(),
        embedded_urls=[fake.url() for _ in range(randint(0, 3))],
        engagements=engagements,
    )

    return item


def fake_response(ids, n_new_items=1):
    new_items = [fake_new_item() for _ in range(n_new_items)]

    ids = list(ids) + [item["id"] for item in new_items]

    return RankingResponse(ranked_ids=ids, new_items=new_items)


def fake_new_item():
    return {
        "id": str(uuid4()),
        "url": f"https://{platform}.com/{fake.random_element(URI_PATHS[platform])}",
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
