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

# ⚠️ Limitations (current version)

* No automatic key rotation (JWT secret-based)
* No distributed pub/sub cache invalidation yet
* No offline policy enforcement (OPA not integrated yet)

---

# 🚀 Roadmap

## Next upgrades

* 🔐 RS256 public/private key JWT system
* ⚡ Redis pub/sub cache invalidation across nodes
* 🧠 Policy engine (OPA integration)
* 🧬 Multi-tenant lab isolation
* 📊 IAM audit logging stream
