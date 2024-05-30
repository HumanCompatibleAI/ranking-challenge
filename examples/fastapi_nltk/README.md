# Basic ranker example (nltk)

This is a toy example that ranks a set of content items based on their sentiment using nltk.

## Data models

This example uses [pydantic](https://docs.pydantic.dev/) to validate the schema for requests and responses.

## Setting up your environment

1. Create a virtual environment using your preferred method
2. `pip install poetry`
3. `poetry install --no-root` at the repo root. This will install only the dependencies listed in `pyproject.toml` without trying to install the current project as a package

## Running tests

Just run `pytest`

## Running the service in development

```bash
uvicorn ranking_server:app --reload
```

This will spin up a server on `http://127.0.0.1:8000`

## Executing your server outside of a unit test

You can start the server and then run `caller.py` to send it data, or you can use the interface provided by FastAPI

## Automatically-generated api docs

With a running server, visit `http://127.0.0.1:8000/docs`. You can send requests from there too.

## Running the service in production

```bash
uvicorn ranking_server:app --host 0.0.0.0 --port 5000
```

## Adding dependencies

To add a new dependency use `poetry add <dependency>` and if it is package specific please move to extra in pyproject.toml
