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
    
class SocmedLean(IntEnum):
    """Enum for social media feed lean"""
    strong_liberal = 1
    moderate_liberal = 2
    neutral = 3
    moderate_conservative = 4
    strong_conservative = 5


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

    feed_lean: Optional[SocmedLean] = Field(
        description="Do you think your social media feeds tend to favour liberal content, conservative content, or neither?"
    )
    
    socmed_censorship: Optional[Literal["not_at_all_likely",  "not_very_likely", "somewhat_likely", "very_likely"]] = Field(
        description="How likely, if at all, do you think it is that social media sites intentionally censor political viewpoints that they find objectionable?"
    )
    
    socmed_trust: Optional[Literal["strongly_distrust", "somewhat_distrust", "neither_trust_nor_distrust", "somewhat_trust", "strongly_trust"]] = Field(
        description="On balance, to what extent do you trust that you receive accurate information from social media?"
    )
    
    percieved_racism: Optional[Literal["Not_a_problem" , "slight_problem" ,"moderate_problem", "significant_problem", "major_problem"]] = Field(
        description="To what extent do you view racism against Black Americans as a problem today?"
    )
    
    trump: Optional[Literal["strongly_unfavorable", "somewhat_unfavorable", "neither_favorable_nor_unfavorable" "somewhat_favorable", "strongly_favorable"]] = Field(
        description="How favorable/unfavorable are your views towards Donald Trump?"
    )
    
    economic: Optional[Literal["extremely_negative", "somewhat_negative", "neither_positive_nor_negative", "somewhat_positive", "extremely_positive"]] = Field(
        description="How positive/negative do you feel about the current U.S. economic situation?"
    )
    
    msm_trust: Optional[Literal["strongly_distrust", "somewhat_distrust", "neither_trust_nor_distrust", "somewhat_trust", "strongly_trust"]] = Field(
        description="How much do you trust mainstream mass media -- such as newspapers, TV and radio – to report the news fully, accurately, and fairly?"
    )
    
    immigration: Optional[Literal["greatly_decreased", "somewhat_decreased", "kept_the_same", "somewhat_increased", "greatly_increased"]] = Field(
        description="In your view, should immigration to the U.S. be increased, decreased, or kept about the same?"
    )
    
    israel_palestine: Optional[Literal["strongly_oppose", "somewhat_oppose", "neither_support_nor_oppose" "somewhat_support", "strongly_support"]] = Field(
        description="How strongly do you support/oppose Israel in the Israeli-Palestinian conflict?"
    )
    
    abortion: Optional[Literal["strongly_oppose", "somewhat_oppose", "neither_support_nor_oppose" "somewhat_support", "strongly_support"]] = Field(
        description="How strongly do you support/oppose the legal right to abortion?"
    )
    
    climate_change: Optional[Literal["not_concerned", "slightly_concerned", "moderately_concerned", "very_concerned", "extremely_concerned"]] = Field(
        description="How concerned are you about climate change?"
    )
    
    military: Optional[Literal["strongly_unfavorable", "somewhat_unfavorable", "neither_favorable_nor_unfavorable" "somewhat_favorable", "strongly_favorable"]] = Field(
        description="How favorable/unfavorable are your views towards the U.S. military?"
    )
    
    political_complexity: Optional[Literal["never", "some_of_the_time", "half_the_time", "most_of_the_time", "always"]] = Field(
        description="How often do politics and government seem so complicated that you can't really understand what's going on?"
    )
    
    political_understanding: Optional[Literal["extremely_well", "very_well",  "moderately_well", "slightly_well", "not_well_at_all"]] = Field(
        description="How well do you understand the important political issues facing our country?"
    )
    
    political_focus: Optional[Literal["never", "some_of_the_time", "half_the_time", "most_of_the_time", "always"]] = Field(
        description="How often do you pay attention to what’s going on in government and politics?"
    )
    
    voting_likelihood: Optional[Literal["will_not_vote", "probably_will_not_vote", "probably_will_vote", "definitely_will_vote"]] = Field(
        description="How likely are you to vote in the general election this November?"
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