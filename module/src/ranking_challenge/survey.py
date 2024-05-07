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
    party_id: Literal[
        "democrat", "republican", "independent", "other", "no_preference"
    ] = Field(
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
