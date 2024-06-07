# Basic ranker example (nltk)

This is a toy example that ranks a set of content items based on their sentiment using nltk.

## Setting up your environment

1. Create a virtual environment using your preferred method
2. `pip install poetry`
3. `poetry install --no-root` at the repo root. This will install only the dependencies listed in `pyproject.toml` without trying to install the current project as a package

## Running tests

Just run `pytest`

## Executing your server outside of a unit test

You can start the server (`python ranking_server.py`), and then run `caller.py` to send it data

## Adding dependencies

To add a new dependency use `poetry add <dependency>` and if it is package specific please move to extra in pyproject.toml
