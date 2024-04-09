import json
import os
import sys
import inspect

parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)

import pytest

from fastapi.testclient import TestClient

from fastapi_nltk import ranking_server
from fastapi_nltk import sample_data


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
        "571775f3-2564-4cf5-b01c-f4cb6bab461b",
        "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
        "a4c08177-8db2-4507-acc1-1298220be98d",
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
    ]

    # check for inserted posts
    assert result["new_items"] == [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
        }
    ]
