from typing import Any, List, Optional, Union, Dict, Callable
from enum import Enum
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess
from prometheus_client import Counter, Gauge, Histogram, Summary
import gzip
import os
import time

class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Starlette,
        registry: CollectorRegistry = None,
        custom_metrics: Dict[str, Callable] = None
    ):
        super().__init__(app)
        self.registry = registry or CollectorRegistry()
        self.custom_metrics = custom_metrics or {}

        # Default metrics ( we can remove these if not needed, just added to depict the use case of default + custom working in tandem)
        self.requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        self.requests_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        status_code = response.status_code
        endpoint = request.url.path

        # Update default metrics
        self.requests_total.labels(request.method, endpoint, status_code).inc()
        self.requests_duration.labels(request.method, endpoint).observe(duration)

        # Update custom metrics
        for metric_func in self.custom_metrics.values():
            metric_func(request, response, duration)

        return response

def expose_metrics(
    app: Starlette,
    should_gzip: bool = False,
    endpoint: str = "/metrics",
    include_in_schema: bool = True,
    tags: Optional[List[Union[str, Enum]]] = None,
    registry: CollectorRegistry = None,
    custom_metrics: Dict[str, Callable] = None,
    **kwargs: Any
) -> None:
    """Exposes endpoint for metrics and adds PrometheusMiddleware.

    Args:
        app: App instance. Endpoint will be added to this app. This can be
            a Starlette app or a FastAPI app.
        should_gzip: Should the endpoint return compressed data? It will
            also check for `gzip` in the `Accept-Encoding` header.
        endpoint: Endpoint on which metrics should be exposed.
        include_in_schema: Should the endpoint show up in the documentation?
        tags: If you manage your routes with tags. Only passed to FastAPI app.
        registry: A custom Prometheus registry to use. If not provided, a
            new CollectorRegistry will be created.
        custom_metrics: A dictionary of custom metric functions to be called
            on each request. Each function should accept (request, response, duration)
            as arguments.
        kwargs: Will be passed to app. Only passed to FastAPI app.
    """
    registry = registry or CollectorRegistry()

    # Add PrometheusMiddleware
    app.add_middleware(PrometheusMiddleware, registry=registry, custom_metrics=custom_metrics)

    def metrics(request: Request) -> Response:
        """Endpoint that serves Prometheus metrics."""
        if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
            multiprocess.MultiProcessCollector(registry)

        if should_gzip and "gzip" in request.headers.get("Accept-Encoding", ""):
            resp = Response(content=gzip.compress(generate_latest(registry)))
            resp.headers["Content-Type"] = CONTENT_TYPE_LATEST
            resp.headers["Content-Encoding"] = "gzip"
        else:
            resp = Response(content=generate_latest(registry))
            resp.headers["Content-Type"] = CONTENT_TYPE_LATEST

        return resp

    # Try to use FastAPI if available, otherwise fall back to Starlette
    try:
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            app.get(endpoint, include_in_schema=include_in_schema, tags=tags, **kwargs)(metrics)
            return
    except ImportError:
        pass

    # Fallback to Starlette
    app.add_route(path=endpoint, route=metrics, include_in_schema=include_in_schema)

# Example of how to define custom metrics
def create_custom_metrics(registry: CollectorRegistry) -> Dict[str, Callable]:
    error_counter = Counter(
        'custom_error_total',
        'Total number of errors',
        ['type'],
        registry=registry
    )

    def update_error_metric(request: Request, response: Response, duration: float):
        if 400 <= response.status_code < 600:
            error_counter.labels(type=str(response.status_code)).inc()

    return {"error_counter": update_error_metric}