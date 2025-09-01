import uuid
import time
from flask import request, g, jsonify
from .models import ApiKey
from .rate_limit import is_rate_limited

def register_middlewares(app):

    @app.before_request
    def before():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())

        if request.path in ["/healthz", "/admin/generate_key"]:
            return

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401

        key_obj = ApiKey.query.filter_by(key=api_key).first()
        if not key_obj or not key_obj.is_valid():
            return jsonify({"error": "Invalid or expired API key"}), 401
        
        if is_rate_limited(api_key):
            return jsonify({"error": "Rate limit exceeded"}), 429

    @app.after_request
    def after(response):
        duration = time.time() - g.start_time
        log_params = {
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        }
        app.logger.info(log_params)
        response.headers["X-Request-ID"] = g.request_id
        return response
