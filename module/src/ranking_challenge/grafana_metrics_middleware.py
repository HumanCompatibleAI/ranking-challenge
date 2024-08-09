import os
import time
import warnings
import requests
import socket
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware

class GrafanaMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        team_id: str,
        push_interval: int = 15,
        *args,
        **kwargs
    ):
        super().__init__(app, *args, **kwargs)
        self.team_id = team_id
        self.push_interval = push_interval
        self.last_push = time.time()
        self.registry = CollectorRegistry()

        # Grafana Cloud configuration
        self.grafana_url = os.getenv('GRAFANA_PUSH_URL')
        self.grafana_username = os.getenv('GRAFANA_USERNAME')
        self.grafana_password = os.getenv('GRAFANA_PASSWORD')

        self.grafana_configured = all([self.grafana_url, self.grafana_username, self.grafana_password])
        
        if not self.grafana_configured:
            warnings.warn("Grafana Cloud credentials not fully configured. Metrics will not be pushed to Grafana.", UserWarning)

        # Example custom metric
        self.custom_metrics = {}

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Check if it's time to push metrics and if Grafana is configured
        if self.grafana_configured and (time.time() - self.last_push > self.push_interval):
            self.push_metrics()
            self.last_push = time.time()

        return response
    
    def get_instance_id(self):
        # Use ECS_TASK_ID environment variable
        ecs_task_id = os.getenv('ECS_TASK_ID')
        if ecs_task_id:
            return ecs_task_id
        
        # Fallback to hostname if ECS_TASK_ID is not set
        warnings.warn("ECS_TASK_ID not set. Falling back to hostname for instance identification.", UserWarning)
        return socket.gethostname()

    def push_metrics(self):
        if self.grafana_configured:
            try:
                push_to_gateway(
                    self.grafana_url,
                    job=f'ranker_metrics_{self.team_id}',
                    registry=self.registry,
                    handler=self._basic_auth_handler
                )
            except Exception as e:
                warnings.warn(f"Failed to push metrics to Grafana: {str(e)}", UserWarning)

    def _basic_auth_handler(self, url, method, timeout, headers, data):
        return requests.request(
            method=method,
            url=url,
            auth=(self.grafana_username, self.grafana_password),
            data=data,
            timeout=timeout,
            headers=headers
        )

    def add_custom_metric(self, metric_name: str, value: float, description: str = ""):
        if metric_name not in self.custom_metrics:
            self.custom_metrics[metric_name] = Gauge(
                f'{self.team_id}_{metric_name}',
                description,
                registry=self.registry
            )
        self.custom_metrics[metric_name].set(value)

        # If Grafana is not configured, log the metric locally
        if not self.grafana_configured:
            print(f"Local metric (not pushed to Grafana): {metric_name} = {value}")