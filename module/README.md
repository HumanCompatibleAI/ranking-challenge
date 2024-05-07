# The Prosocial Ranking Challenge

The Prosocial Ranking Challenge is designed to inspire, fund, and test the best algorithms to improve well-being, polarization, and factual knowledge for social media users. We will use our browser extension to re-order the feeds of paid U.S. participants on Facebook, Reddit, and X (Twitter) for four months, and measure changes in attitudes and behavior.

[More about the project here](https://humancompatible.ai/news/2024/01/18/the-prosocial-ranking-challenge-60000-in-prizes-for-better-social-media-algorithms/)

How do we identify pro- and anti-social content? That's where you come in! We are soliciting ranking algorithms to test, with $60,000 in prize money to be split between ten finalists (as selected by our panel of experts).

## pydantic models for the PRC API schema

You can use these models in your Python code, both to generate valid data, and to parse incoming data.

Using the models ensures that your data has been at least somewhat validated. If the schema changes and your code needs an update, you're more likely to be able to tell right away.

### Parsing a request

#### With FastAPI

If you're using fastapi, you can use the models right in your server:

```python
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse

@app.post("/rank")
def rank(ranking_request: RankingRequest) -> RankingResponse:
    ...
    # You can return a RankingResponse here, or a dict with the correct keys and
    # pydantic will figure it out.
```

If you specify `RankingResponse` as your reeturn type, you will get validation of your response for free.

For a complete example, check out `../fastapi_nltk/`

#### Otherwise

If you'd like to parse a request directly, here is how:

```python
from ranking_challenge.request import RankingRequest

loaded_request = RankingRequest.model_validate_json(json_data)
```

### Generating fake data

There is a fake data generator, `rcfaker`. If you run it directly it'll print some.

You can also import it like so:

```python
from ranking_challenge.fake import fake_request, fake_response

# 5 fake reddit posts with 2 comments each
request = fake_request(n_posts=5, n_comments=2, platform='reddit')

# corresponding ranker response with 2 added items
request_ids = [r.id for r in request]
response = fake_response(request_ids, n_new_items=2)
```

For more in-depth examples, check out the tests.

### More

[The pydantic docs](https://docs.pydantic.dev/latest/)
