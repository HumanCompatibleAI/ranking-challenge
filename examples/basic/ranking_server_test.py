import pytest

from basic import ranking_server, sample_data


@pytest.fixture
def app():
    app = ranking_server.app
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_rank(client):
    # Send POST request to the API
    response = client.post("/rank", json=sample_data.BASIC_EXAMPLE)

    # Check if the request was successful (status code 200)
    assert response.status_code == 200

    # Check if the response is a list of ids
    assert isinstance(response.json, list)

    # Check if the response contains the expected ids, in the expected order
    assert response.json == [
        "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
        "a4c08177-8db2-4507-acc1-1298220be98d",
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
    ]
