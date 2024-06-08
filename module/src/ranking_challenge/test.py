# ruff: noqa: E501
from enum import IntEnum
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class IdeologyEnum(IntEnum):
    """Enum for ideology"""

    extremely_liberal = 1
    liberal = 2
    slightly_liberal = 3
    moderate = 4
    slightly_conservative = 5
    conservative = 6
    extremely_conservative = 7


class AgeEnum(IntEnum):
    """Enum for age brackets"""

    eighteen_to_twenty_four = 1
    twenty_five_to_thirty_four = 2
    thirty_five_to_forty_four = 3
    forty_five_to_fifty_four = 4
    fifty_five_to_sixty_four = 5
    sixty_five_and_older = 6


class EducationEnum(IntEnum):
    """Enum for education levels"""

    some_high_school = 1
    graduated_high_school = 2
    some_college = 3
    associate_degree = 4
    bachelor_degree = 5
    graduate_degree = 6


class IncomeEnum(IntEnum):
    """Enum for income brackets"""

    less_than_20k = 1
    twenty_to_thirty_five_k = 2
    thirty_five_to_fifty_k = 3
    fifty_to_seventy_five_k = 4
    seventy_five_to_one_hundred_k = 5
    one_hundred_to_one_hundred_fifty_k = 6
    one_hundred_fifty_k_and_up = 7


class SocmedUseEnum(IntEnum):
    """Enum for social media usage"""

    zero_to_thirty_minutes = 1
    thirty_to_sixty_minutes = 2
    sixty_to_ninety_minutes = 3
    ninety_to_one_twenty_minutes = 4
    two_to_three_hours = 5
    three_to_four_hours = 6
    more_than_four_hours = 7


class SurveyResponse(BaseModel):
    """
    Response to PRC survey.

    Scalar quantities are represented as IntEnums, while categorical questions are represented as strings constrained with Literal.

    These will be added to the request by the PRC request router, since this data is not available to the browser extension.
    """

    # Demographic metrics
    party_id: Literal["democrat", "republican", "independent", "other", "no_preference"] = Field(
        description="Generally speaking, do you usually think of yourself as a Republican, Democrat, Independent, etc?"
    )

    party_write_in: Optional[str] = Field(
        description="If you selected 'other' for your party identification, please specify.",
        default=None,
    )

    support: Literal["strong", "not_strong"] = Field(
        description="Would you call yourself a strong or not a very strong supporter of your party?"
    )

    party_lean: Literal["democrat", "republican"] = Field(
        description="Do you think of yourself as closer to the Republican or Democratic party?"
    )

    sex: Literal["female", "male", "nonbinary", "prefer_not_to_say"]

    age: AgeEnum = Field(description="What age are you?")

    education: EducationEnum = Field(
        description="What is the highest level of education you have completed?"
    )

    ideology: IdeologyEnum = Field(
        description="Here is a scale on which the political views that people might hold are arranged from liberal to conservative. Where would you place yourself on this scale?"
    )

    income: IncomeEnum = Field(description="What is your annual household income?")

    ethnicity: Literal[
        "native_american",
        "asian_or_pacific_islander",
        "black_or_african_american",
        "hispanic_or_latino",
        "white_or_caucasian",
        "multiple_or_other",
    ] = Field(description="Which race or ethnicity best describes you?")

    ethnicity_write_in: Optional[str] = Field(
        description="If you selected 'multiple' or 'other' for your ethnicity, please specify.",
        default=None,
    )

    socmed_use: SocmedUseEnum = Field(
        description="Think of the past two weeks. How much time did you spend on social media, on average, per day?"
    )

    browser_perc: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            description="In the last two weeks, what percentage of your social media [twitter/facebook/reddit] has been on a desktop device or laptop?",
        ),
    ]

    mobile_perc: Annotated[
        float,
        Field(
            ge=0,
            le=1,
            description="In the last two weeks, what percentage of your social media [twitter/facebook/reddit] has been on mobile device?",
        ),
    ]

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


class NewItem(BaseModel):
    """A new item to be inserted into the feed"""

    id: str = Field(
        description="A unique ID for the content item. You can generate this.",
        default_factory=uuid4,
    )
    url: HttpUrl = Field(description="The publicly-accessible URL of the content item.")


class RankingResponse(BaseModel):
    """A response to a ranking request"""

    ranked_ids: list[str] = Field(
        description="The IDs of the content items, in the order they should be displayed."
    )
    new_items: Optional[list[NewItem]] = Field(
        description="New publicly-accessible items to be inserted into the feed.",
        default=None,
    )
# ruff: noqa: E501
from datetime import datetime
from typing import Literal, Optional, Union
# from typing_extensions import Annotated, deprecated
import warnings

from pydantic import BaseModel, Field, HttpUrl
from pydantic.types import NonNegativeInt


class TwitterEngagements(BaseModel):
    """Engagement counts from Twitter"""

    retweet: NonNegativeInt
    like: NonNegativeInt
    comment: NonNegativeInt
    share: NonNegativeInt


class RedditEngagements(BaseModel):
    """Engagement counts from Reddit"""

    warnings.warn('The upvotes and `downvotes` field is deprecated as it is net of upvotes and downvotes; use `score` instead.', DeprecationWarning)
    upvote: Optional[NonNegativeInt]
    downvote: Optional[NonNegativeInt]
    score: Optional[NonNegativeInt]
    comment: NonNegativeInt
    award: NonNegativeInt


class FacebookEngagements(BaseModel):
    """Engagement counts from Facebook"""

    like: NonNegativeInt
    love: NonNegativeInt
    care: NonNegativeInt
    haha: NonNegativeInt
    wow: NonNegativeInt
    sad: NonNegativeInt
    angry: NonNegativeInt
    comment: NonNegativeInt
    share: NonNegativeInt


class ContentItem(BaseModel):
    """A content item to be ranked"""

    id: str = Field(
        description="A unique ID describing a specific piece of content. We will do our best to make an ID for a given item persist between requests, but that property is not guaranteed."
    )

    original_rank: Optional[NonNegativeInt] = Field(
        description="The rank of the item in the original feed. Useful for debugging and analysis of performance.",
        default=None
    )
    
    post_id: Optional[str] = Field(
        description="The ID of the post to which this comment belongs. Useful for linking comments to their post when comments are shown in a feed. Currently this UX only exists on Facebook.",
        default=None,
    )

    parent_id: Optional[str] = Field(
        description="For threaded comments, this identifies the comment to which this one is a reply. Blank for top-level comments.",
        default=None,
    )

    title: Optional[str] = Field(
        description="The post title, only available on reddit posts.", default=None
    )

    text: str = Field(
        description="The text of the content item. Assume UTF-8, and that leading and trailing whitespace have been trimmed."
    )

    author_name_hash: str = Field(
        description="A hash of the author's name (salted). Use this to determine which posts are by the same author. When the post is by the current user, this should match `session.user_name_hash`."
    )

    type: Literal["post", "comment"] = Field(
        description="Whether the content item is a `post` or `comment`. On Twitter, tweets will be identified as `comment` when they are replies displayed on the page for a single tweet."
    )

    embedded_urls: Optional[list[HttpUrl]] = Field(
        description="A list of URLs that are embedded in the content item. This could be links to images, videos, or other content. They may or may not also appear in the text of the item."
    )

    created_at: datetime = Field(
        description="The time that the item was created in UTC, in `YYYY-MM-DD hh:mm:ss` format, at the highest resolution available (which may be as low as the hour)."
    )

    engagements: Union[TwitterEngagements, RedditEngagements, FacebookEngagements] = Field(
        description="Engagement counts for the content item."
    )

class Session(BaseModel):
    """Data that is scoped to the user's browsing session (generally a single page view)"""

    session_id: str = Field(
        description="A unique ID for this page view, updated on navigation events. Use this to determine if two requests came from the same page."
    )
    user_id: str = Field(
        description="A unique id for this study participant. Will remain fixed for the duration of the experiment."
    )
    user_name_hash: str = Field(
        description="A (salted) hash of the user's username. We'll do our best to make it match the `item.author_name_hash` on posts authored by the current user."
    )
    cohort: str = Field(
        description="The cohort to which the user has been assigned. You can safely ignore this. It is used by the PRC request router."
    )
    
    cohort_index: Optional[NonNegativeInt] = Field(
        description="The index of the cohort to which the user has been assigned. Used to select cohort when request comes through.",
        
    )
    platform: Literal["twitter", "reddit", "facebook"] = Field(
        description="The platform on which the user is viewing content."
    )
    url: HttpUrl = Field(
        description="The URL of the page that the user is viewing, minus the query string portion. This can help you to determine which part of the application the user is in."
    )
    current_time: datetime = Field(
        description="The current time according to the user's browser, in UTC, in `YYYY-MM-DD hh:mm:ss` format."
    )


class RankingRequest(BaseModel):
    """A complete ranking request"""

    session: Session = Field(description="Data that is scoped to the user's browsing session")
    survey: Optional[SurveyResponse] = Field(
        description="Responses to PRC survey. Added by the request router.",
        default=None,
    )
    items: list[ContentItem] = Field(description="The content items to be ranked.")


import hashlib
import time
from random import randint
from uuid import uuid4

from faker import Faker

fake = Faker(locale="la")  # remove locale to get rid of the fake latin

URI_PATHS = {
    "reddit": ["", "r/aww", "r/politics", "r/programming", "r/technology"],
    "twitter": ["", "jack", "TiredActor", "horse_ebooks"],
    "facebook": ["", "photo", "groups"],
}


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
            session_id=str(uuid4()),
            url=f"https://{platform}.com/{fake.random_element(URI_PATHS[platform])}",
            user_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
            cohort="AB",
            cohort_index=randint(0,4096),
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
            "score": randint(0, 50),
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
