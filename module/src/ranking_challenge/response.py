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

class RankingResponseMetadata(BaseModel):
    """"Additional information about the ranking process, stored by client"""

    intervention_on: Optional[bool] = Field(
        description="False if intevention configured off, user in control group, or error occurred",
        default=None
    )

class RankingResponse(BaseModel):
    """A response to a ranking request"""

    ranked_ids: list[str] = Field(
        description="The IDs of the content items, in the order they should be displayed."
    )
    new_items: Optional[list[NewItem]] = Field(
        description="New publicly-accessible items to be inserted into the feed.",
        default=None,
    )
    metadata: Optional[RankingResponseMetadata] = Field(
        description="Additional information about the ranking process, stored by client.",
        default=None,
    )

