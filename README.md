# API Gateway

A small API gateway in Python that puts routing, API-key authentication, rate limiting, and upstream failure handling in one place. Two sample services make the request path easy to follow locally.

**Python · Flask · PostgreSQL · Redis · Prometheus**

## Request flow

```text
Client → API key check → Redis rate limit → Proxy → Upstream service
             │                                │
         PostgreSQL                      Retry / circuit breaker
                                              │
                                  Request logs + Prometheus metrics
```

PostgreSQL stores API keys and their validity. Redis counts requests per key and service. The proxy forwards requests to the upstreams in `gateway_config.yaml`, while middleware records response status, duration, and a request ID.

## Implementation highlights

- **Shared request policy:** authentication and rate limiting run before service handlers.
- **Fixed-window quotas:** separate limits for the two sample services, configured over a 60-second window.
- **Failure handling:** up to three attempts for request exceptions, exponential backoff, and a per-service circuit breaker with a cooldown.
- **Observability:** an `X-Request-ID` response header, request logs, a request counter, and a latency histogram at `/metrics`.
- **Small modules:** routing, persistence, rate limiting, metrics, and proxy behavior can be read independently.

## Run locally

Use Python 3.10+ with a local PostgreSQL database and Redis instance. The example below assumes a database named `gateway` and a database user that can create tables in it.

```bash
git clone https://github.com/coganka/api-gateway.git
cd api-gateway
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create `.env` in the repository root, replacing the example database credentials and master key:

```dotenv
DEBUG=false
DATABASE_URL=postgresql://gateway_user:local_password@localhost:5432/gateway
REDIS_URL=redis://localhost:6379/0
MASTER_KEY=replace-with-a-local-development-secret
```

The app creates its tables at startup. Run each process in a separate terminal, from the repository root with the virtual environment activated:

```bash
python services/service1.py  # port 5001
python services/service2.py  # port 5002
python app.py               # gateway on port 8000
```

Create an API key using the same master key as your `.env`:

```bash
curl -X POST http://localhost:8000/admin/generate_key \
  -H 'X-Master-Key: replace-with-a-local-development-secret' \
  -H 'Content-Type: application/json' \
  -d '{"owner":"local-demo"}'
```

Copy the returned `api_key` into the request:

```bash
curl http://localhost:8000/service1/test -H 'X-API-Key: YOUR_RETURNED_KEY'
curl http://localhost:8000/healthz
curl http://localhost:8000/metrics
```

The proxied test returns `{"service":"service1","status":"ok"}`. Missing or invalid keys return `401`; an exhausted quota returns `429`.

## Code map

| File | Responsibility |
|---|---|
| [gateway/routes.py](gateway/routes.py) | Admin endpoints and dynamic proxy routes |
| [gateway/middleware.py](gateway/middleware.py) | Authentication, service lookup, request logging, metrics |
| [gateway/proxy.py](gateway/proxy.py) | Upstream HTTP calls and retries |
| [gateway/rate_limit.py](gateway/rate_limit.py) | Redis counters and expiry |
| [gateway/circuit_breaker.py](gateway/circuit_breaker.py) | Failure counts and cooldown state |

## Design boundaries

This is a compact implementation of gateway mechanics. The current service detection in middleware recognizes `service1` and `service2`; adding an upstream to YAML also requires updating that detection for quotas and metric labels.

Circuit-breaker state is local to each Python process. It counts exhausted request exceptions, not upstream HTTP 5xx responses. The proxy does not currently preserve query strings, and retries apply to all supported methods; safe retries for requests with side effects need an explicit idempotency policy. API keys are stored in plaintext, and the admin endpoint uses a shared master key.

Useful next steps are integration tests for these failure paths, hashed key storage, and a complete local container setup. No throughput or production availability guarantees are claimed.
