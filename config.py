import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/gateway")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVICE_MAP = {
        "/service1": os.getenv("SERVICE1_URL", "http://localhost:5001"),
        "/service2": os.getenv("SERVICE2_URL", "http://localhost:5002"),
    }

    MASTER_KEY = os.getenv("MASTER_KEY", "supersecret")

    #rate limiting
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))  
    RATE_PERIOD = int(os.getenv("RATE_PERIOD", "60")) 

