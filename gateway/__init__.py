from flask import Flask
from config import Config
from .routes import bp, register_service_routes
from .db import db
from .rate_limit import init_redis
from .middleware import register_middlewares

def create_app():
    app = Flask(__name__)

    cfg = Config()
    app.config["SERVICE_MAP"] = cfg.SERVICE_MAP
    app.config["RATE_LIMITS"] = cfg.RATE_LIMITS
    app.config["RATE_PERIOD"] = cfg.RATE_PERIOD
    app.config["DEBUG"] = cfg.DEBUG
    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = cfg.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["MASTER_KEY"] = cfg.MASTER_KEY
    app.config["REDIS_URL"] = cfg.REDIS_URL

    db.init_app(app)
    with app.app_context():
        db.create_all()

    init_redis(app)
    register_middlewares(app)

    register_service_routes(app)
    app.register_blueprint(bp)

    return app
