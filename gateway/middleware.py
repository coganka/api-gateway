import uuid
import time
from flask import request, g, jsonify
from .models import ApiKey
from .rate_limit import is_rate_limited
from .metrics import REQUEST_COUNT, REQUEST_LATENCY


def register_middlewares(app):

    @app.before_request
    def before():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())

        #skip
        if request.path in ["/healthz", "/admin/generate_key", "/metrics"]:
            return

        # api key auth
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401

        key_obj = ApiKey.query.filter_by(key=api_key).first()
        if not key_obj or not key_obj.is_valid():
            return jsonify({"error": "Invalid or expired API key"}), 401

        # rate limit
        service = None
        if request.path.startswith("/service1"):
            service = "service1"
        elif request.path.startswith("/service2"):
            service = "service2"

        if service and is_rate_limited(api_key, service):
            return jsonify({"error": "Rate limit exceeded"}), 429


    @app.after_request
    def after(response):
        duration = time.time() - g.start_time
        # log
        log_params = {
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        }
        app.logger.info(log_params)
        response.headers["X-Request-ID"] = g.request_id

        # metrics
        service = "unknown"
        if request.path.startswith("/service1"):
            service = "service1"
        elif request.path.startswith("/service2"):
            service = "service2"

        REQUEST_COUNT.labels(service=service, method=request.method, status=response.status_code).inc()
        REQUEST_LATENCY.labels(service=service).observe(duration)

        return response
