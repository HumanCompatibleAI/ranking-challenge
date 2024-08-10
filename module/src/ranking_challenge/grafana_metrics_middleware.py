import os
import time
import warnings
import requests
import logging
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.openmetrics.exposition import generate_latest
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GrafanaMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        team_id: str,
        push_interval: int = 10,
        *args,
        **kwargs
    ):
        super().__init__(app, *args, **kwargs)
        self.team_id = team_id
        self.push_interval = push_interval
        self.last_push = time.time()
        self.registry = CollectorRegistry()

        logger.info(f"Initializing GrafanaMetricsMiddleware with team_id: {team_id}, push_interval: {push_interval}")

        # Grafana Cloud configuration
        self.grafana_url = os.getenv('GRAFANA_PUSH_URL')
        self.grafana_username = os.getenv('GRAFANA_USERNAME')
        self.grafana_password = os.getenv('GRAFANA_PASSWORD')

        self.grafana_configured = all([self.grafana_url, self.grafana_username, self.grafana_password])
        
        if self.grafana_configured:
            logger.info(f"Grafana Cloud credentials configured successfully. Push URL: {self.grafana_url}")
        else:
            logger.warning("Grafana Cloud credentials not fully configured. Metrics will not be pushed to Grafana.")

        # Custom metrics
        self.custom_metrics = {}

    async def dispatch(self, request: Request, call_next):
        logger.debug("Dispatching request")
        response = await call_next(request)

        # Check if it's time to push metrics and if Grafana is configured
        if self.grafana_configured and (time.time() - self.last_push > self.push_interval):
            logger.info(f"Push interval reached ({self.push_interval}s), attempting to push metrics")
            self.push_metrics()
            self.last_push = time.time()

        return response

    def push_metrics(self):
        if self.grafana_configured:
            try:
                logger.debug("Generating metrics data")
                metrics_data = generate_latest(self.registry)
                logger.info(f"Pushing metrics to Grafana: {self.grafana_url}")
                
                # Method 1: Using requests
                response = requests.post(
                    self.grafana_url,
                    data=metrics_data,
                    auth=(self.grafana_username, self.grafana_password),
                    headers={'Content-Type': 'application/x-protobuf'},
                    timeout=10
                )
                logger.debug(f"Push response status code: {response.status_code}")
                logger.debug(f"Push response content: {response.text}")
                
                if response.status_code == 204:
                    logger.info("Successfully pushed metrics to Grafana using requests")
                else:
                    logger.warning(f"Failed to push metrics to Grafana using requests. Status code: {response.status_code}")
                
                # Method 2: Using push_to_gateway
                try:
                    push_to_gateway(self.grafana_url, job=self.team_id, registry=self.registry)
                    logger.info("Successfully pushed metrics to Grafana using push_to_gateway")
                except Exception as e:
                    logger.error(f"Failed to push metrics using push_to_gateway: {str(e)}")
                
                # Method 3: Custom JSON payload
                json_metrics = {}
                for metric in self.registry.collect():
                    for sample in metric.samples:
                        json_metrics[sample.name] = sample.value
                
                json_response = requests.post(
                    self.grafana_url,
                    json=json_metrics,
                    auth=(self.grafana_username, self.grafana_password),
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                logger.debug(f"JSON push response status code: {json_response.status_code}")
                logger.debug(f"JSON push response content: {json_response.text}")
                
                if json_response.status_code == 204:
                    logger.info("Successfully pushed metrics to Grafana using JSON")
                else:
                    logger.warning(f"Failed to push metrics to Grafana using JSON. Status code: {json_response.status_code}")
                
            except Exception as e:
                logger.error(f"Failed to push metrics to Grafana: {str(e)}", exc_info=True)

    def add_custom_metric(self, metric_name: str, value: float, description: str = "", labels: dict = None):
        logger.debug(f"Adding custom metric: {metric_name}, value: {value}, description: {description}, labels: {labels}")
        
        if labels is None:
            labels = {}
        
        labels['team_id'] = self.team_id

        instance_id = os.getenv('ECS_TASK_ID')
        if instance_id:
            labels['instance_id'] = instance_id
            logger.debug(f"Added instance_id to labels: {instance_id}")

        metric_key = (metric_name, tuple(sorted(labels.items())))
        
        if metric_key not in self.custom_metrics:
            logger.info(f"Creating new Gauge for metric: {metric_name}")
            self.custom_metrics[metric_key] = Gauge(
                metric_name,
                description,
                labelnames=list(labels.keys()),
                registry=self.registry
            )
        
        self.custom_metrics[metric_key].labels(**labels).set(value)
        logger.debug(f"Set value for metric {metric_name}: {value}")

        # Log metric locally
        labels_str = ', '.join(f"{k}={v}" for k, v in labels.items())
        logger.info(f"Metric added (not yet pushed to Grafana): {metric_name}{{{labels_str}}} = {value}")

logger.info("Enhanced GrafanaMetricsMiddleware module loaded")