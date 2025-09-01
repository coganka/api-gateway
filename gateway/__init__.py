from flask import Flask
from config import Config
from .routes import bp
from .middleware import register_middlewares
from .db import db
from .rate_limit import init_redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    init_redis(app)
    register_middlewares(app)
    app.register_blueprint(bp)

    return app
