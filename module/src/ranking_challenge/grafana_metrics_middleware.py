import os
import time
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GrafanaMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        team_id: str,
        push_interval: int = 5,  # Temporarily reduced for testing
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
            logger.debug(f"GRAFANA_PUSH_URL: {'SET' if self.grafana_url else 'NOT SET'}")
            logger.debug(f"GRAFANA_USERNAME: {'SET' if self.grafana_username else 'NOT SET'}")
            logger.debug(f"GRAFANA_PASSWORD: {'SET' if self.grafana_password else 'NOT SET'}")

        # Custom metrics
        self.custom_metrics = {}

    async def dispatch(self, request: Request, call_next):
        logger.debug("Dispatching request")
        response = await call_next(request)

        # Check if it's time to push metrics and if Grafana is configured
        current_time = time.time()
        if self.grafana_configured and (current_time - self.last_push > self.push_interval):
            logger.info(f"Push interval reached ({self.push_interval}s), attempting to push metrics")
            self.push_metrics()
            self.last_push = current_time
        else:
            logger.debug(f"Not pushing metrics. Time since last push: {current_time - self.last_push:.2f}s")

        return response

    def push_metrics(self):
        if self.grafana_configured:
            try:
                logger.debug("Preparing to push metrics to Grafana")
                
                # Use push_to_gateway instead of manual POST request
                push_to_gateway(
                    self.grafana_url,
                    job=f'team_{self.team_id}',
                    registry=self.registry,
                    handler=self.grafana_auth_handler
                )
                
                logger.info("Successfully pushed metrics to Grafana")
            except Exception as e:
                logger.error(f"Failed to push metrics to Grafana: {str(e)}", exc_info=True)
        else:
            logger.warning("Grafana not configured, skipping metric push")

    def grafana_auth_handler(self, url, method, timeout, headers, data):
        logger.debug(f"Calling Grafana auth handler. URL: {url}, Method: {method}")
        return basic_auth_handler(url, method, timeout, headers, data, self.grafana_username, self.grafana_password)

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

    def force_push_metrics(self):
        logger.info("Manually triggering metric push")
        self.push_metrics()

logger.info("Debug-Enhanced GrafanaMetricsMiddleware module loaded")