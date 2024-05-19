"""This is a test harness used in development of the scoring job queue.

It can be used to prototype scoring flows independent of the rest of the
ranking pipeline; it is janky and provided mostly for the convenience of the
PRC dev team; use and modify it freely if you find it helpful.
"""

import requests
import time
from itertools import count


URL = "http://localhost:8002/score"


def datagen(n, task_latency_sec):
    counter = count()
    for _ in range(n):
        yield dict(
            item_id=str(next(counter)),
            text="asdf",
            sleep=task_latency_sec,
        )


def do_request():
    request = {
        "data": list(datagen(10, 0.1)),
    }
    start = time.time()
    result = requests.post(URL, json=request)
    data = result.json()["data"]
    network_time = time.time() - start
    max_time = max(x["timings"]["RANDOM"]["result_received"] for x in data)
    # print(result.text)
    # print(f"Elapsed: {time.time() - start}")
    print(network_time, max_time)


if __name__ == "__main__":
    do_request()
