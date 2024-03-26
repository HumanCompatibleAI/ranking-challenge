import sys

sys.path.append(".")  # allows for importing from the current directory

import pytest

import ranking_server
import sample_data


@pytest.fixture
def app():
    app = ranking_server.app
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_rank(client):
    # Send POST request to the API
    response = client.post("/rank", json=sample_data.CHATGPT_EXAMPLE)

    # Check if the request was successful (status code 200)
    assert response.status_code == 200

    # Check if the response is a dictionary
    assert isinstance(response.json, dict)

    # Check if the response contains the expected ids, in the expected order
    assert response.json["ranked_ids"] == [
        "571775f3-2564-4cf5-b01c-f4cb6bab461b",
        "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
        "a4c08177-8db2-4507-acc1-1298220be98d",
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
    ]

    # check for inserted posts
    assert response.json["new_items"] == [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
        }
    ]
