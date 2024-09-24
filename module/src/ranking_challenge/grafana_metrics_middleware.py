import os
import time
import warnings
import requests
import logging
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GrafanaMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        job_name: str,
        team_id: str,
        push_interval: int = 5,
        *args,
        **kwargs
    ):
        super().__init__(app, *args, **kwargs)
        self.job_name = job_name
        self.team_id = team_id
        self.push_interval = push_interval
        self.last_push = time.time()
        self.registry = CollectorRegistry()

        logger.info(f"Initializing GrafanaMetricsMiddleware with job_name: {job_name}, team_id: {team_id}, push_interval: {push_interval}")


        # Custom metrics
        self.custom_metrics = {}
        
        # Grafana Cloud configuration
        self.grafana_url = os.getenv('GRAFANA_PUSH_URL')
        self.grafana_username = os.getenv('GRAFANA_USERNAME')
        self.grafana_password = os.getenv('GRAFANA_PASSWORD')

        self.grafana_configured = all([self.grafana_url, self.grafana_username, self.grafana_password])
        
        if self.grafana_configured:
            logger.info(f"Grafana Cloud credentials configured successfully. Push URL: {self.grafana_url}")
        else:
            logger.warning("Grafana Cloud credentials not fully configured. Metrics will not be pushed to Grafana.")

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        current_time = time.time()
        if self.grafana_configured and (current_time - self.last_push > self.push_interval):
            logger.debug(f"Push interval reached. Last push: {self.last_push}, Current time: {current_time}")
            self.push_metrics()
            self.last_push = current_time
        else:
            logger.debug(f"Not pushing metrics. Time since last push: {current_time - self.last_push:.2f}s")

        return response

    def push_metrics(self):
        if self.grafana_configured:
            try:
                logger.debug(f"Preparing to push metrics to Grafana: {self.grafana_url}")
                
                # Construct the correct URL for pushing metrics
                push_url = f"{self.grafana_url.rstrip('/')}/metrics/job/{self.job_name}"
                
                data = generate_latest(self.registry)
                
                headers = {
                    'Content-Type': 'application/x-protobuf',
                    'X-Prometheus-Remote-Write-Version': '0.1.0'
                }
                
                response = requests.post(
                    push_url,
                    data=data,
                    auth=(self.grafana_username, self.grafana_password),
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully pushed metrics to Grafana. Status code: {response.status_code}")
                else:
                    logger.error(f"Failed to push metrics. Status code: {response.status_code}, Response: {response.text}")
                
            except Exception as e:
                logger.error(f"Failed to push metrics to Grafana: {str(e)}", exc_info=True)
        else:
            logger.warning("Grafana not configured, skipping metric push")

    def add_custom_metric(self, metric_name: str, value: float, description: str = "", labels: dict = None):
        logger.debug(f"Adding custom metric: {metric_name}, value: {value}, description: {description}, labels: {labels}")
        
        if labels is None:
            labels = {}
        
        labels['job'] = self.job_name
        labels['team'] = self.team_id
        labels['instance'] = os.getenv('HOSTNAME', 'unknown')

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

    def force_push_metrics(self):
        logger.info("Manually triggering metric push")
        self.push_metrics()

logger.info("Debug-Enhanced GrafanaMetricsMiddleware module loaded")