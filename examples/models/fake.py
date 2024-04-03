import hashlib
import inspect
import os
from random import randint
import sys
import time
from uuid import uuid4

parentdir = os.path.dirname(  # make it possible to import from ../ in a reliable way
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
sys.path.insert(0, parentdir)

from faker import Faker

fake = Faker(locale="la")  # remove locale to get rid of the fake latin

from models.request import ContentItem, RankingRequest, Session
from models.response import RankingResponse

def fake_request(n_items=1):
    return RankingRequest(
        session=Session(
            user_id=str(uuid4()),
            user_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
            platform="reddit",
            current_time=time.time(),
        ),
        items=[fake_item() for _ in range(n_items)]

    )

def fake_item():
    return ContentItem(
        id=str(uuid4()),
        text=fake.text(),
        author_name_hash=hashlib.sha256(fake.name().encode()).hexdigest(),
        type="post",
        created_at=time.time(),
        engagements={
            "upvote": randint(0, 50),
            "downvote": randint(0, 50),
            "comment": randint(0, 50),
            "award": randint(0, 50)
        },
    )

def fake_response(ids, n_new_items=1):
    new_items = [fake_new_item() for _ in range(n_new_items)]

    ids = list(ids) + [item["id"] for item in new_items]

    return RankingResponse(
        ranked_ids=ids,
        new_items=new_items
    )

def fake_new_item():
    return {
        "id": str(uuid4()),
        "url": fake.url(),
    }

# if run from command line
if __name__ == "__main__":
    request = fake_request(3)
    print("Request:")
    print(request.model_dump_json(indent=2))

    # use ids from request
    response = fake_response([item.id for item in request.items], 2)
    print("\nResponse:")
    print(response.model_dump_json(indent=2))
