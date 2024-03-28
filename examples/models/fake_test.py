import os
import sys
import inspect

parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)

from models import fake

def test_fake_request():
    # this test's purpose is mostly to run the code to make sure it doesn't
    # have any validation errors
    request = fake.fake_request(5)
    assert len(request.items) == 5

    # all ids are unique
    assert len(set(item.id for item in request.items)) == 5

def test_fake_response():
    ids = [str(i) for i in range(5)]

    response = fake.fake_response(ids, 2)
    assert len(response.ranked_ids) == 7

    # all ids are unique
    assert len(set(id for id in response.ranked_ids)) == 7
