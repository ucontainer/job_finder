"""Anti-ban utilities for web scraping — delays, proxy rotation, user agent rotation."""

from __future__ import annotations

import random
import time

from backend.config import PROXY_LIST

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
]


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def get_random_proxy() -> str | None:
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)
