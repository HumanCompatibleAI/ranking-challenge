# ruff: noqa: E501
from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl
from pydantic.types import NonNegativeInt

from .survey import SurveyResponse


class TwitterEngagements(BaseModel):
    """Engagement counts from Twitter"""

    retweet: NonNegativeInt
    like: NonNegativeInt
    comment: NonNegativeInt
    share: NonNegativeInt


class RedditEngagements(BaseModel):
    """Engagement counts from Reddit"""

    upvote: Optional[NonNegativeInt] = Field(
        description="The reddit upvote field is deprecated, use score instead",
        deprecated=True,
        default=None,
    )
    downvote: Optional[NonNegativeInt] = Field(
        description="The reddit downvote field is deprecated, use score instead",
        deprecated=True,
        default=None,
    )
    score: Optional[int] = Field(
        description="The reddit post score (sum of upvote/downvote)", default=None
    )
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
        default=None,
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
    cohort: Optional[str] = Field(
        description="The cohort to which the user has been assigned. You can most likely ignore this. It is used by the PRC request router."
    )
    cohort_index: Optional[NonNegativeInt] = Field(
        description="The user's randomly-assigned cohort index. You can ignore this. The request router uses it to place users into buckets (cohorts).",
        default=None,
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
