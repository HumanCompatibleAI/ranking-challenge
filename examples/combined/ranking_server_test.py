import json
import pytest

from fastapi.testclient import TestClient
import fakeredis

import ranking_server
import test_data


@pytest.fixture
def app():
    app = ranking_server.app
    yield app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_rank(client, redis_client):
    # Send POST request to the API
    response = client.post("/rank", json=test_data.BASIC_EXAMPLE)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        assert False

    result = response.json()

    # Check if the response contains the expected ids, in the expected order
    assert result["ranked_ids"][1:4] == [
        "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
        "a4c08177-8db2-4507-acc1-1298220be98d",
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
    ]

    # check for inserted posts
    assert len(result["new_items"]) == 1
