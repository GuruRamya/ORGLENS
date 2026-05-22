import json
import hashlib
import redis
from app.config import settings

_redis = redis.from_url(settings.redis_url)

def _cache_key(org_id: str, message_hash: str) -> str:
    return f"orglens:scores:{org_id}:{message_hash}"

def get_message_hash(messages: list[dict]) -> str:
    content = "".join(sorted(m.get("content", "") for m in messages[:100]))
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def get_cached_scores(org_id: str, message_hash: str) -> dict | None:
    key = _cache_key(org_id, message_hash)
    raw = _redis.get(key)
    return json.loads(raw) if raw else None

def cache_scores(org_id: str, message_hash: str, scores: dict, ttl: int = 86400):
    key = _cache_key(org_id, message_hash)
    _redis.setex(key, ttl, json.dumps(scores))