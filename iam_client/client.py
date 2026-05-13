import json
import httpx
import redis
from jose import jwt
from typing import Optional

from .models import UserContext


class AsyncIAMClient:
    def __init__(self, base_url: str, redis_url: str = "redis://localhost:6379"):
        self.base_url = base_url.rstrip("/")
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.http = httpx.AsyncClient(timeout=3)

    # ----------------------------
    # L0: LOCAL JWT VALIDATION
    # ----------------------------
    def decode_local(self, token: str, secret: str) -> dict:
        return jwt.decode(token, secret, algorithms=["HS256"])

    # ----------------------------
    # L1: CACHE CHECK
    # ----------------------------
    def get_cached_user(self, token: str) -> Optional[UserContext]:
        cached = self.redis.get(f"iam:{token}")

        if cached:
            return UserContext(**json.loads(cached))

        return None

    def set_cache(self, token: str, user: dict, ttl: int = 300):
        self.redis.setex(
            f"iam:{token}",
            ttl,
            json.dumps(user)
        )

    def evict_cache(self, token: str):
        try:
            self.redis.delete(f"iam:{token}")
        except Exception:
            pass

    # ----------------------------
    # L2: AUTH SERVICE FALLBACK
    # ----------------------------
    async def validate_remote(self, token: str) -> Optional[UserContext]:
        try:
            res = await self.http.post(
                f"{self.base_url}/auth/validate",
                json={"token": token}
            )

            data = res.json()

            # 🔥 CACHE EVICTION ON INVALID TOKEN
            if not data.get("valid"):
                self.evict_cache(token)
                return None

            user = {
                "user_id": data["user_id"],
                "email": data["email"],
                "roles": data.get("roles", []),
                "permissions": data.get("permissions", []),
                "valid": True
            }

            self.set_cache(token, user)
            return UserContext(**user)

        except Exception:
            return None

    # ----------------------------
    # MAIN ENTRY (ZERO LATENCY PATH)
    # ----------------------------
    async def get_user(self, token: str, secret: str) -> Optional[UserContext]:

        # 1. CACHE HIT (fastest path)
        cached = self.get_cached_user(token)
        if cached:
            return cached

        # 2. LOCAL JWT VALIDATION (no network)
        try:
            payload = self.decode_local(token, secret)
        except Exception:
            return None

        user = {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", []),
            "valid": True
        }

        # 3. CACHE RESULT
        self.set_cache(token, user)

        return UserContext(**user)