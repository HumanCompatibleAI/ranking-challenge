from datetime import datetime, UTC
import json
from unittest.mock import patch

import fakeredis
from fastapi.testclient import TestClient
import pytest

import ranking_server
import test_data


@pytest.fixture
def app(redis_client):
    with patch("ranking_server.redis_client", return_value=redis_client):
        app = ranking_server.app
        yield app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def redis_client(request):
    redis_client = fakeredis.FakeRedis()
    return redis_client


def test_rank(client, redis_client):
    # put named entities in redis
    result_key = "my_worker:scheduled:top_named_entities"

    fake_named_entities = ['foo', 'bar', 'baz']
    redis_client.set(
        result_key,
        json.dumps(
            {
                "top_named_entities": fake_named_entities,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ),
    )

    # Send POST request to the API
    response = client.post("/rank", json=test_data.BASIC_EXAMPLE)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        assert False

    result = response.json()

    # Check if the response contains the expected ids, in the expected order
    assert result["ranked_ids"] == [
        "should-rank-high",
        "should-rank-high-2",
        "should-rank-low",
    ]
