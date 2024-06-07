# Ranker integration test

A somewhat-complete integration test for a ranker. This is what we are using for basic functional evaluation of a first-round submission.

## Setting up your environment

1. Create a virtual environment using your preferred method
2. `pip install poetry`
3. `poetry install --no-root` at the repo root. This will install only the dependencies listed in `pyproject.toml` without trying to install the current project as a package

## Running the test

Run it on a ranking endpoint like so:

```bash
pytest -rP --url http://localhost:8000/rank
```

You can run it on any publicly-accessible url, but to test it out, try one of the code examples in this repo!

## What this is testing for?

### Correctness

When provided with a valid request, the ranker should return a valid response. It shouldn't fail or return invalid json.

There should be items in the response. If new items are added, they should be used in the ranking. All returned item IDs should be unique.

### Performance

During the first round, we are not overly concerned about performance. However, the test does have a 30 second request timeout. We expect to rank as many as 100 items in a batch, and even a prototype ranker should be able to complete that in 30 seconds. Keep in mind that finalists will have an SLA for the same task of 500ms p95.
