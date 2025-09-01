import os
from dotenv import load_dotenv
from gateway.config_loader import load_config

load_dotenv()

class Config:
    def __init__(self):
        cfg = load_config()

        self.SERVICE_MAP = {f"/{name}": svc["url"] for name, svc in cfg["services"].items()}
        self.RATE_LIMITS = {f"/{name}": svc.get("rate_limit", 100) for name, svc in cfg["services"].items()}
        self.RATE_PERIOD = cfg["settings"].get("rate_period", 60)

        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/gateway")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.MASTER_KEY = os.getenv("MASTER_KEY", "supersecret")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
