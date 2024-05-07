from ranking_challenge import fake
from ranking_challenge.request import RankingRequest


def test_fake_request():
    # this test's purpose is mostly to run the code to make sure it doesn't
    # have any validation errors. pydantic will make sure it has the right fields.
    request = fake.fake_request(n_posts=5)
    assert len(request.items) == 5

    # all ids are unique
    assert len(set(item.id for item in request.items)) == 5

    request = fake.fake_request(n_posts=5, n_comments=2, platform="twitter")
    assert len(request.items) == 15
    assert request.session.platform == "twitter"


def test_fake_response():
    ids = [str(i) for i in range(5)]

    response = fake.fake_response(ids, 2)
    assert len(response.ranked_ids) == 7

    # all ids are unique
    assert len(set(id for id in response.ranked_ids)) == 7


def test_load_fake_data():
    # This really just exercises pydantic, and is mostly an example
    # of how to load json data
    request = fake.fake_request(5)
    json_data = request.model_dump_json()

    loaded_request = RankingRequest.model_validate_json(json_data)
    assert len(loaded_request.items) == 5
