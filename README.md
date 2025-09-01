# API Gateway

A lightweight **API Gateway** built with Flask, Postgres, and Redis — inspired by Kong/Envoy but implemented from scratch to showcase production-grade backend concepts.  

This gateway acts as a **traffic cop** for microservices:
- Routes requests to backend services
- Authenticates clients via API keys
- Applies per-client rate limits
- Handles backend failures with retries and a circuit breaker
- Logs requests with correlation IDs
- Exposes a `/metrics` endpoint for observability (Prometheus-ready)
- Configuration driven via `gateway_config.yaml`

---

## ✨ Features
- **Reverse Proxy** – dynamic routing to multiple backend services  
- **API Key Authentication** – keys stored in Postgres, generated via admin API  
- **Rate Limiting** – Redis-based counters, per-service quotas  
- **Resilience** – retries with exponential backoff, circuit breaker for failing backends  
- **Logging** – structured logs with request IDs and latency  
- **Observability** – Prometheus metrics (requests, errors, latency)  
- **Config-driven** – add/remove services via `gateway_config.yaml`  

---

## 🛠 Tech Stack
- [Flask](https://flask.palletsprojects.com/) – HTTP server & middleware  
- [Postgres](https://www.postgresql.org/) – persistent API key storage  
- [Redis](https://redis.io/) – rate limiting & caching  
- [Prometheus](https://prometheus.io/) – metrics collection  
- [Docker Compose](https://docs.docker.com/compose/) (optional, future) – run full stack easily  

---

## 🚀 Getting Started

### 1. Clone repo & install deps
```bash
git clone https://github.com/coganka/api-gateway.git
cd api-gateway
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup environment
Create `.env`:
```env
DEBUG=true

DATABASE_URL=postgresql://gateway_user:gateway_pass@localhost:5432/gateway
MASTER_KEY=supersecret

REDIS_URL=redis://localhost:6379/0
```

### 3. Create `gateway_config.yaml`
```yaml
services:
  service1:
    url: "http://localhost:5001"
    rate_limit: 100
  service2:
    url: "http://localhost:5002"
    rate_limit: 50

settings:
  rate_period: 60
```

### 4. Run services and gateway
```bash
python services/service1.py
python services/service2.py
python app.py
```

---

## 🔑 Usage

### Generate API Key
```bash
curl -X POST http://localhost:8000/admin/generate_key \
  -H "X-Master-Key: supersecret" \
  -H "Content-Type: application/json" \
  -d '{"owner":"test-client"}'
```

### Call Service Through Gateway
```bash
curl http://localhost:8000/service1/test -H "X-API-Key: <your_api_key>"
```

### Metrics
```bash
curl http://localhost:8000/metrics
```

---

## 📊 Example Prometheus Metrics

```
# HELP gateway_requests_total Total requests through gateway
# TYPE gateway_requests_total counter
gateway_requests_total{service="service1",method="GET",status="200"} 5.0

# HELP gateway_request_latency_seconds Request latency through gateway
# TYPE gateway_request_latency_seconds histogram
gateway_request_latency_seconds_bucket{service="service1",le="0.005"} 1.0
```
