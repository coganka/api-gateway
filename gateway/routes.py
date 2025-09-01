import uuid
from flask import Blueprint, request, jsonify, current_app
from .proxy import forward_request
from .models import ApiKey
from .db import db
from .metrics import metrics_endpoint

bp = Blueprint("gateway", __name__)

#  system endpoints
@bp.route("/healthz")
def health():
    return {"status": "ok"}

@bp.route("/metrics")
def metrics():
    return metrics_endpoint()

#  admin API (generate new API keys) 
@bp.route("/admin/generate_key", methods=["POST"])
def generate_key():
    master_key = request.headers.get("X-Master-Key")
    if master_key != current_app.config["MASTER_KEY"]:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    owner = data.get("owner", "unknown")
    new_key = uuid.uuid4().hex

    api_key = ApiKey(key=new_key, owner=owner)
    db.session.add(api_key)
    db.session.commit()

    return {"api_key": new_key, "owner": owner}

#  dynamic service routes 
def register_service_routes(app):
    for prefix, upstream in app.config["SERVICE_MAP"].items():
        service_name = prefix.lstrip("/") 

        def handler(path="", upstream=upstream, service_name=service_name):
            target_url = f"{upstream}/{path}" if path else upstream
            return forward_request(target_url, service_name)

        endpoint_base = f"{service_name}_handler"

        bp.add_url_rule(
            f"{prefix}/",
            defaults={"path": ""},
            view_func=handler,
            methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            endpoint=f"{endpoint_base}_root",
        )

        bp.add_url_rule(
            f"{prefix}/<path:path>",
            view_func=handler,
            methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            endpoint=f"{endpoint_base}_subpath",
        )

