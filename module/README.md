# The Prosocial Ranking Challenge

The Prosocial Ranking Challenge is designed to inspire, fund, and test the best algorithms to improve well-being, polarization, and factual knowledge for social media users. We will use our browser extension to re-order the feeds of paid U.S. participants on Facebook, Reddit, and X (Twitter) for four months, and measure changes in attitudes and behavior.

[More about the project here](https://humancompatible.ai/news/2024/01/18/the-prosocial-ranking-challenge-60000-in-prizes-for-better-social-media-algorithms/)

How do we identify pro- and anti-social content? That's where you come in! We are soliciting ranking algorithms to test, with $60,000 in prize money to be split between ten finalists (as selected by our panel of experts).

# Prometheus Metrics Middleware

This middleware provides an easy way to add Prometheus metrics to your rankers. It automatically exposes a `/metrics` endpoint that can be scraped by Prometheus and logged in Grafana.

## What are these metrics for?

Prometheus metrics allow you to monitor and analyze various aspects of your ranker's performance and behavior. These metrics can be visualized in Grafana, allowing you to gain insights into your ranker's health, performance, and usage patterns.

## How it works

1. The middleware collects and stores metrics data as your application runs.
2. A `/metrics` endpoint is added to your application.
3. When this endpoint is accessed (by a Prometheus server), it serves the collected metrics data in the Prometheus text-based format.
4. Prometheus periodically scrapes this endpoint to collect the latest metrics.

This follows Prometheus' pull model, where PRC metrics service polls and fetches metrics from your ranker, rather than your ranker pushing metrics.

## Installation

```bash
pip install ranking_challenge prometheus_client
```

## Usage

Here's how to set up the middleware and define custom metrics:

```python
from starlette.applications import Starlette
from fastapi import FastAPI
from ranking_challenge.prometheus_metrics_otel_middleware import (
    expose_metrics,
    CollectorRegistry,
)
from prometheus_client import Counter, Histogram

# Your app can be either Starlette or FastAPI
app = FastAPI()

# Create a registry
registry = CollectorRegistry()

# Create custom metrics
custom_metrics = create_custom_metrics(registry)

# Define a custom metric
content_score = Histogram('content_score', 'Distribution of content scores', ['platform'], registry=registry)

# Define a function to update the custom metric
def update_content_score(request, response, duration):
    # This is just an example. In a real ranker, you'd get these values from your actual logic.
    score = 0.75  # Example score
    platform = "mobile"  # Example platform
    content_score.labels(platform=platform).observe(score)

# Add the custom metric to the dictionary
custom_metrics["content_score"] = update_content_score

# Set up the metrics endpoint and middleware
expose_metrics(
    app,
    endpoint="/metrics",
    registry=registry,
    custom_metrics=custom_metrics
)

# Your application routes and logic go here
@app.route("/")
async def root():
    return {"message": "Hello World"}
```

In this example, we're creating a histogram metric to track the distribution of content scores across different platforms. Every time a request is processed, the `update_content_score` function will be called, which updates our custom metric.

## Metric Types

Prometheus supports several types of metrics. You'll need to import these from `prometheus_client` for use. The most common are:

1. **Counter**: A cumulative metric that only goes up (e.g., number of requests)
2. **Gauge**: A metric that can go up and down (e.g., current number of active sessions)
3. **Histogram**: Samples observations and counts them in configurable buckets (e.g., request durations)
4. **Summary**: Similar to histogram, but calculates configurable quantiles over a sliding time window

Example Usage:
```
from prometheus_client import Counter, Histogram
```

For more details on metric types, refer to the [Prometheus documentation](https://prometheus.io/docs/concepts/metric_types/).

## Viewing Metrics

Once set up and deployed to production, you can view and analyze the raw metrics in Grafana Cloud under your team's folder.


## Learn More

- [Prometheus Data Model Concept](https://prometheus.io/docs/concepts/data_model/)
- [Grafana](https://grafana.com/)

## pydantic models for the PRC API schema

You can use these models in your Python code, both to generate valid data, and to parse incoming data.

Using the models ensures that your data has been at least somewhat validated. If the schema changes and your code needs an update, you're more likely to be able to tell right away.

### Parsing a request

#### With FastAPI

If you're using fastapi, you can use the models right in your server:

```python
from ranking_challenge.request import RankingRequest
from ranking_challenge.response import RankingResponse

@app.post("/rank")
def rank(ranking_request: RankingRequest) -> RankingResponse:
    ...
    # You can return a RankingResponse here, or a dict with the correct keys and
    # pydantic will figure it out.
```

If you specify `RankingResponse` as your reeturn type, you will get validation of your response for free.

For a complete example, check out `../fastapi_nltk/`

#### Otherwise

If you'd like to parse a request directly, here is how:

```python
from ranking_challenge.request import RankingRequest

loaded_request = RankingRequest.model_validate_json(json_data)
```

### Generating fake data

There is a fake data generator, `rcfaker`. If you run it directly it'll print some.

You can also import it like so:

```python
from ranking_challenge.fake import fake_request, fake_response

# 5 fake reddit posts with 2 comments each
request = fake_request(n_posts=5, n_comments=2, platform='reddit')

# corresponding ranker response with 2 added items
request_ids = [r.id for r in request]
response = fake_response(request_ids, n_new_items=2)
```

For more in-depth examples, check out the tests.

### More

[The pydantic docs](https://docs.pydantic.dev/latest/)