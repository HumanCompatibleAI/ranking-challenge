from datetime import datetime
import sys

sys.path.append(".")  # allows for importing from the current directory

import pytest
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from unittest.mock import patch

import ranking_server
import sample_data


@pytest.fixture
def app():
    app = ranking_server.app
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@patch("ranking_server.client.chat.completions")
def test_rank(openai_mock, client):
    openai_response = '[ {"item_idx": 1, "reason": "The statement is very positive."}, {"item_idx": 2, "reason": "The statement is somewhat positive."}, {"item_idx": 0, "reason": "The statement is negative."} ]'
    openai_mock.create.return_value = mock_completion(openai_response)

    # Send POST request to the API
    response = client.post("/rank", json=sample_data.CHATGPT_EXAMPLE)

    # Check if the request was successful (status code 200)
    assert response.status_code == 200

    # Check if the response is a dictionary
    assert isinstance(response.json, dict)

    # Check if the response contains the expected ids, in the expected order
    assert response.json["ranked_ids"] == [
        "571775f3-2564-4cf5-b01c-f4cb6bab461b",
        "1fcbb164-f81f-4532-b068-2561941d0f63",
        "s5ad13266-8abk4-5219-kre5-2811022l7e43dv",
        "a4c08177-8db2-4507-acc1-1298220be98d",
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
    ]

    # check for inserted posts
    assert response.json["new_items"] == [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
        },
        {
            "id": "1fcbb164-f81f-4532-b068-2561941d0f63",
            "url": "https://reddit.com/r/PRCExample/comments/ef56a23/another_example_to_insert",
        },
    ]


def mock_completion(content, model="gpt-3.5-turbo"):
    completion = ChatCompletion(
        id="foo",
        model=model,
        object="chat.completion",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=content,
                    role="assistant",
                ),
                text="foo",
            )
        ],
        created=int(datetime.now().timestamp()),
    )

    return completion
