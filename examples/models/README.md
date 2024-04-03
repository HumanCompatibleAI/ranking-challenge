# pydantic models for the PRC API schema

You can use these models in your Python code, both to generate valid data, and to parse incoming data.

Using the models ensures that your data has been at least somewhat validated. If the schema changes your code needs an update, you're more likely to be able to tell right away.

## Parsing a request

### With FastAPI

If you're using fastapi, you can use the models right in your server:

```python
from models.request import RankingRequest
from models.response import RankingResponse

@app.post("/rank")
def rank(ranking_request: RankingRequest) -> RankingResponse:
    ...
    # You can return a RankingResponse here, or a dict with the correct keys and
    # pydantic will figure it out.
```

If you specify `RankingResponse` as your reeturn type, you will get validation of your response for free.

### Otherwise

If you'd like to parse a request directly, here is how:

```python
from models.request import RankingRequest

loaded_request = RankingRequest.model_validate_json(json_data)
```

## Generating fake data

There is a fake data generator in `fake.py`. If you run it, it will print some. You can also import it

## More

[The pydantic docs](https://docs.pydantic.dev/latest/)
