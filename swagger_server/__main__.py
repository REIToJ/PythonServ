#!/usr/bin/env python3

import connexion
from swagger_server import encoder
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from prometheus_client import start_http_server, Counter, Gauge
import time
import logging
from flask.logging import default_handler
import os
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
            # You can add more fields here as needed
        }
        return json.dumps(log_record)
    
# Create a gauge metric for server uptime
uptime_gauge = Gauge('api_uptime_seconds', 'Server uptime in seconds')

def setup_opentelemetry():
    # Configure tracing
    trace_provider = TracerProvider()
    trace.set_tracer_provider(trace_provider)

    # Configure Jaeger Exporter
    jaeger_exporter = JaegerExporter(
        # You can customize the endpoint and other parameters if needed
        agent_host_name='localhost',
        agent_port=6831,
    )

    trace_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )   
    tracer = trace.get_tracer(__name__)

    # Configure metrics
    console_exporter = ConsoleMetricExporter()
    metric_reader = PeriodicExportingMetricReader(console_exporter)
    metrics_provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(metrics_provider)
# Get the absolute path to the 'logs' folder
logs_folder = os.path.join(os.path.dirname(__file__), 'logs')

# Ensure the 'logs' folder exists
os.makedirs(logs_folder, exist_ok=True)
# Set up logging to write logs to a file in the 'logs' folder
log_file_path = os.path.join(logs_folder, 'app.log')
# Import your OpenTelemetry code here
# Set up logging to use the JsonFormatter
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    log_handler = logging.FileHandler('lokiprom/app.log')
    log_handler.setFormatter(JsonFormatter())

    logger.addHandler(log_handler)
    logger.addHandler(default_handler)  # Keep the default handler if needed

    logger.info("App started")
    
def main():
    setup_opentelemetry()
    setup_logging()
    # Start the Prometheus metrics server on a separate port
    start_http_server(8000)

    # Create a meter from the global meter provider
    meter = metrics.get_meter("game_shop_meter")

    # Create and use synchronous instruments
    work_counter = meter.create_counter(
        "work.counter", unit="1", description="Counts the amount of work done"
    )
    def do_work(work_item):
        # Count the work being done
        work_counter.add(1, {"work.type": work_item.work_type})
        print("doing some work...")
     # Periodically update the uptime gauge
    def update_uptime():
        while True:
            uptime_seconds = time.time() - start_time
            uptime_gauge.set(uptime_seconds)
            time.sleep(15)  # Update every 15 seconds

    # Start the update_uptime task in a separate thread
    import threading
    uptime_thread = threading.Thread(target=update_uptime)
    uptime_thread.start()
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Game Shop API'}, pythonic_params=True)
   
    app.run(port=8080)

if __name__ == '__main__':
    start_time = time.time()
    main()
