from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import Response

REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total requests through gateway",
    ["service", "method", "status"]
)

REQUEST_LATENCY = Histogram(
    "gateway_request_latency_seconds",
    "Request latency through gateway",
    ["service"]
)

def metrics_endpoint():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
