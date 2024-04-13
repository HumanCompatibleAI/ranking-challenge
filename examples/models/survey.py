from pydantic import BaseModel, validator, ValidationError
from typing import Optional

class EnumField:
    """Dictionaries for conversion of likert to enum"""
    
    support_conv = {
        "Strong": 1,
        "Not very strong": 0,
    }
    
    ideology_conv = {
        "Extremely liberal": 1,
        "Liberal": 2,
        "Slightly liberal" : 3,
        "Moderate, middle of the road" : 4,
        "Slightly conservative" : 5,
        "Conservative" : 6,
        "Extremely conservative": 7
    }
    
    outparty_persp_conv = {
        "Strongly agree": 1,
        "Agree": 2,
        "Neutral": 3,
        "Disagree": 4,
        "Strongly disagree": 5
    }
    
    social_trust_conv = {
        "Cannot trust": 0,
        "Can trust": 1,
        "It depends": 2,
        "Unsure": 3
    }
    
    wellbeing_conv = {
        "All of the time": 1,
        "Most of the time": 2,
        "More than half of the time": 3,
        "Some of the time": 4,
        "At no time": 5
    }
    
    news_knowledge_conv = {
        "True": True,
        "False": False,
        "Unsure": None
    }
    
    fb_reddit_x_conv = {
        "Yes": True,
        "No": False,
        "Not sure": None
    }
    
class SurveyResponses(BaseModel):
    """Responses to PRC survey. Values are converted using EnumField dictionaries where necessary."""
    
    # Demographic metrics
    party_id: str
    support: int # Accept strong as 1, not strong as 0
    lean: str
    
    # Conversion of support into int
    @validator('support', pre=True)
    def convert_support(cls, value):
        if value in EnumField.support_conv:
            return EnumField.support_conv[value]
        raise ValueError("Invalid value")
    
    sex: str
    age: str
    ethnicity: str
    education: str
    ideology: int 
    income :str
    socmed: str
    browser_perc: float
    mobile_perc: float
    
    # conversion of idealogy likert into dictionary
    @validator('ideology', pre=True)
    def convert_ideology(cls, value):
        if value in EnumField.ideology_conv:
            return EnumField.ideology_conv[value]
        raise ValueError("Invalid value")
    
    # Conflict metrics
    outparty_sentiment: int
    inparty_sentiment: int
    inparty_violence: int
    inparty_harassment: int
    outparty_violence: int
    outparty_harassment: int
    outparty_protest: int
    outparty_pov_perspective: int 
    outparty_pov_importance: int
    social_trust: int 
    outparty_friendship: int 
    inparty_friendship: int 
    
    # Conversions of outparty_pov_perspective, outparty_pov_importance, social_trust into int
    @validator('outparty_pov_perspective', 'outparty_pov_importance', pre=True)
    def convert_outparty(cls, value):
        if value in EnumField.outparty_persp_conv:
            return EnumField.outparty_persp_conv[value]
        raise ValueError("Invalid value")
    
    @validator('social_trust', pre=True)
    def convert_trust(cls, value):
        if value in EnumField.social_trust_conv:
            return EnumField.social_trust_conv[value]
        raise ValueError("Invalid value")   
    
    # Wellbeing metrics
    cheerful: int 
    calm: int 
    active: int 
    well_rested: int 
    stimulated: int 
    fb_meaningful: Optional[bool]
    x_meaningful: Optional[bool]
    reddit_meaningful: Optional[bool]
    fb_negative: Optional[bool]
    x_negative: Optional[bool]
    reddit_negative: Optional[bool]
       
    # Conversion of wellbeing metrics into int  
    @validator('cheerful', 'calm', 'active', 'well_rested', 'stimulated', pre=True)
    def convert_wellbeing(cls, value):
        if value in EnumField.wellbeing_conv:
            return EnumField.wellbeing_conv[value]
        raise ValueError("Invalid value")      

    
    # Information
    
    # Cannot encode with boolean due to 'unsure' option. Alternative is nullable boolean?
     
    headline_1 : Optional[bool]
    headline_2 : Optional[bool]
    headline_3 : Optional[bool]
    headline_4 : Optional[bool]
    headline_5 : Optional[bool]
    headline_6 : Optional[bool]
    headline_7 : Optional[bool]
    headline_8 : Optional[bool]
    headline_9 : Optional[bool]
    headline_10 : Optional[bool]
    
    learned_fb : Optional[bool]
	learned_x : Optional[bool]
	learned_reddit : Optional[bool]
	harmful_fb : Optional[bool]
	harmful_x : Optional[bool]
	harmful_reddit : Optional[bool]
 
    # Conversion of news_knowledge into boolean
    @validator('headline_1', 'headline_2', 'headline_3', 'headline_4', 'headline_5', 'headline_6', 'headline_7',
               'headline_8', 'headline_9', 'headline_10', pre=True)
    def convert_news_knowledge(cls, value):
        if value in EnumField.news_knowledge_conv:
            return EnumField.news_knowledge_conv[value]
        raise ValueError("Invalid value")
    
    # Conversion of social metrics into int
    @validator('fb_meaningful', 'x_meaningful', 'reddit_meaningful', 'fb_negative', 'x_negative', 'reddit_negative',
               'learned_fb', 'learned_x', 'learned_reddit', 'harmful_fb', 'harmful_x', 'harmful_reddit',  pre=True)
    def convert_socials(cls, value):
        if value in EnumField.fb_reddit_x_conv:
            return EnumField.fb_reddit_x_conv[value]
        raise ValueError("Invalid value") 

