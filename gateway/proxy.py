import requests
import time
from flask import request, Response, jsonify, current_app
from .circuit_breaker import CircuitBreaker


breaker = CircuitBreaker()

def forward_request(target_url: str, service_name="service"):
    headers = {k: v for k, v in request.headers if k.lower() != "host"}

    if breaker.is_blocked(service_name):
        return jsonify({"error": f"{service_name} temporarily unavailable"}), 503

    for attempt in range(3):
        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                timeout=5,
            )
            breaker.record_success(service_name)
            return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
        except requests.exceptions.RequestException as e:
            wait = 0.2 * (2 ** attempt)
            time.sleep(wait)
            if attempt == 2:  
                breaker.record_failure(service_name)
                return jsonify({"error": "Backend unavailable"}), 502
