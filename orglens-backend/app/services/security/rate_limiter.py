"""
Simple in-memory rate limiter.
No Redis required.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, Request


RATE_LIMIT_STORAGE = defaultdict(list)


def rate_limit(
    scope: str,
    max_calls: int = 10,
    window_seconds: int = 60
):

    async def _check(request: Request):

        user_id = (
            getattr(request.state, "user_id", None)
            or request.client.host
        )

        key = f"{scope}:{user_id}"

        now = time.time()

        RATE_LIMIT_STORAGE[key] = [
            timestamp
            for timestamp in RATE_LIMIT_STORAGE[key]
            if timestamp > now - window_seconds
        ]

        if len(RATE_LIMIT_STORAGE[key]) >= max_calls:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

        RATE_LIMIT_STORAGE[key].append(now)

        print("CALL COUNT:", len(RATE_LIMIT_STORAGE[key]))

    return _check
