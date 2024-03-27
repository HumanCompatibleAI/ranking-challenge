# Chat GPT example (using OpenAI API)

This is another simple example that uses the OpenAI API to rank items based on their emotional valence.

## Setting up your environment

1. Create a virtual environment using your preferred method
2. `pip install -r requirements.txt`

## Running tests

Just run `pytest`. For some systems, depending on your environment architecture, you can also try `python -m pytest`. 

## Executing your server outside of a unit test

You can start the server (`python ranking_server.py`), and then run `caller.py` to send it data