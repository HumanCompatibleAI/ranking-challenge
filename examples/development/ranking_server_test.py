import json
import sys

sys.path.append(".")  # allows for importing from the current directory

import pytest
from fastapi.testclient import TestClient

from development import ranking_server, sample_data


@pytest.fixture
def app():
    app = ranking_server.app
    yield app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_rank(client):
    # Send POST request to the API
    response = client.post("/rank", json=sample_data.BASIC_EXAMPLE)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        assert False

    result = response.json()

    # Check if the response contains the expected ids, in the expected order
    assert result["ranked_ids"] == [
        "a4c08177-8db2-4507-acc1-1298220be98d",
        "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
    ]
