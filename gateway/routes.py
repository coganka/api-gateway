import uuid
from flask import Blueprint, request, jsonify, current_app
from .proxy import forward_request
from .models import ApiKey
from .db import db


bp = Blueprint("gateway", __name__)


@bp.route("/healthz")
def health():
    return {"status": "ok"}


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


@bp.route("/service1/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@bp.route("/service1/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def service1(path):
    upstream = current_app.config["SERVICE_MAP"]["/service1"]
    target_url = f"{upstream}/{path}" if path else upstream
    return forward_request(target_url, "service1")


@bp.route("/service2/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@bp.route("/service2/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def service2(path):
    upstream = current_app.config["SERVICE_MAP"]["/service2"]
    target_url = f"{upstream}/{path}" if path else upstream
    return forward_request(target_url, "service2")
