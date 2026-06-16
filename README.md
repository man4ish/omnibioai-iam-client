# 🔐 OmniBioAI IAM Client

A **high-performance, async Identity & Access Management (IAM) client SDK** for the OmniBioAI ecosystem.

It provides **zero-latency authentication**, combining:

* Local JWT validation
* Redis caching layer
* Async fallback to central auth service

---

# 🚀 Overview

This SDK is designed to securely authenticate and authorize users across distributed OmniBioAI services:

* TES (HPC workflow engine)
* Workbench (Django platform)
* Control Center (system observability)
* Studio (Electron desktop client)
* SDK integrations

It ensures **sub-millisecond identity checks for HPC-scale workloads**.

---

## Deployment Context

The IAM client is used as a **library**, not a standalone service.
It is embedded in services that need to validate JWT tokens:

- `omnibioai-api-gateway` — validates every incoming request
- `omnibioai-security-sdk` — wraps IAM client in middleware stack
- `omnibioai-control-center` — validates internal service tokens

Install as a local package:

```bash
pip install -e ~/Desktop/machine/omnibioai-iam-client
```

---

# ⚡ Key Features

## 🧠 Zero-latency authentication

* Cache-first identity resolution
* Local JWT decoding (no network required)

## ⚡ Async + scalable

* Built on `httpx.AsyncClient`
* Non-blocking authentication flow

## 🧩 Redis caching layer

* Token → user context caching
* Automatic TTL-based expiration
* Cache eviction on invalid tokens

## 🔐 Secure fallback model

* Central auth service validation when cache misses
* Revocation-aware token handling

---

# 🏗 Architecture

```text
Client Request
      │
      ▼
Redis Cache (FAST PATH ⚡)
      │ hit
      ▼
User Context returned (0.5 ms)

      │ miss
      ▼
Local JWT decode (NO NETWORK)
      │ success
      ▼
Cache store

      │ fallback
      ▼
Auth Service validation
      │
      ▼
Cache update / eviction
```

---

## Testing

```bash
cd ~/Desktop/machine/omnibioai-iam-client
pytest tests/ -v --cov=.

# 100% coverage
# Covers: IAM client validate, cache hit/miss,
#         token eviction, permission checks, models
```

---

# 📦 Installation

```bash
pip install httpx redis python-jose pydantic
```

Or install locally:

```bash
pip install -e .
```

---

# ⚙️ Usage

## Initialize IAM Client

```python
from iam_client import AsyncIAMClient

iam = AsyncIAMClient(
    base_url="http://auth-service:8001",
    redis_url="redis://localhost:6379"
)
```

---

## Authenticate user (HPC-safe)

```python
user = await iam.get_user(
    token=ACCESS_TOKEN,
    secret="JWT_SECRET"
)

if not user:
    raise Exception("Unauthorized")
```

---

## Access user context

```python
print(user.user_id)
print(user.email)
print(user.roles)
```

---

# ⚡ Performance Model

| Layer                 | Latency   |
| --------------------- | --------- |
| Redis cache           | ~0.3–1 ms |
| Local JWT decode      | ~0.2 ms   |
| Auth service fallback | ~20–80 ms |

👉 99% requests never hit network

---

# 🔐 Security Model

## Token validation layers

1. Cache validation (fast path)
2. Local JWT validation (offline)
3. Central auth validation (fallback)

## Cache invalidation

* Invalid tokens are immediately removed from Redis
* Revoked tokens are not cached again

---

# 🧠 Design Principles

* Zero-trust authentication
* Fail-safe by default
* HPC-first performance design
* Stateless compute nodes
* Centralized identity authority

---

# 🧬 Integration Targets

This SDK is used across:

* omnibioai-tes
* omnibioai
* omnibioai-control-center
* omnibioai-workbench

---

## Known Limitations

- No automatic key rotation (JWT secret-based, rotation planned for v0.5)
- No offline policy enforcement (OPA not integrated)

> **Note:** Redis pub/sub cache invalidation IS implemented —
> the api-gateway subscribes to `policy:invalidate` and evicts
> stale tokens on logout. This is handled at the gateway level,
> not the IAM client level.

---

## Roadmap

| Feature | Status |
|---------|--------|
| Redis cache-first validation | ✓ Stable |
| Async httpx client | ✓ Stable |
| Local JWT decode (offline) | ✓ Stable |
| Cache eviction on invalid tokens | ✓ Stable |
| Redis pub/sub invalidation (gateway level) | ✓ Stable |
| 100% test coverage | ✓ Stable |
| RS256 public/private key JWT | Planned v0.5 |
| Multi-tenant lab isolation | Planned v0.5 |
| OPA policy integration | Planned |

---

## Related Services

| Service | Role |
|---------|------|
| `omnibioai-auth` | Validates tokens on cache miss (POST /auth/validate) |
| `omnibioai-api-gateway` | Primary consumer — uses IAM client for every request |
| `omnibioai-security-sdk` | Wraps IAM client in reusable middleware |
| `omnibioai-studio` | Provides REDIS_URL and IAM_URL via docker-compose env |

## License

Apache 2.0

---

*Part of the [OmniBioAI](https://github.com/man4ish/omnibioai-studio) platform.*
