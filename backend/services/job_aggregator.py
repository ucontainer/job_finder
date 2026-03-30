"""Job aggregation service — fetches postings from real job board APIs."""

from __future__ import annotations

import hashlib
import logging
import time

import requests

from backend.config import RAPIDAPI_KEY, SCRAPING_ENABLED
from backend.models.schemas import JobPosting
from backend.utils.anti_ban import get_random_user_agent, random_delay

logger = logging.getLogger(__name__)

# In-memory cache: key → (timestamp, results)
_cache: dict[str, tuple[float, list[JobPosting]]] = {}
CACHE_TTL = 3600  # 1 hour


def _cache_key(job_title: str, location: str) -> str:
    return hashlib.sha256(f"{job_title.lower()}|{location.lower()}".encode()).hexdigest()


def fetch_jobs(job_title: str, location: str) -> list[JobPosting]:
    """Fetch job postings for a given title and location.

    Tries JSearch API first, falls back to scraping if enabled.
    Results are cached for CACHE_TTL seconds.
    """
    key = _cache_key(job_title, location)
    if key in _cache:
        ts, cached = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return cached

    jobs: list[JobPosting] = []

    # --- JSearch API (primary source) ---
    jobs.extend(_fetch_from_jsearch(job_title, location))

    # --- Scraping fallback ---
    if not jobs and SCRAPING_ENABLED:
        jobs.extend(_scrape_jobs(job_title, location))

    if not jobs:
        logger.warning(
            "No jobs found for '%s' in '%s'. "
            "Check that RAPIDAPI_KEY is set in your .env file.",
            job_title,
            location,
        )

    _cache[key] = (time.time(), jobs)
    return jobs


def _fetch_from_jsearch(job_title: str, location: str) -> list[JobPosting]:
    """Fetch real job postings from JSearch API (via RapidAPI).

    Free tier: 200 requests/month.
    Sign up at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
    """
    if not RAPIDAPI_KEY:
        logger.warning("RAPIDAPI_KEY not set — skipping JSearch API.")
        return []

    query = f"{job_title} in {location}" if location else job_title

    headers = {
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "User-Agent": get_random_user_agent(),
    }

    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "month",  # only recent postings
    }

    try:
        random_delay(0.3, 0.8)  # light delay to be respectful
        response = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.error("JSearch API request failed: %s", exc)
        return []

    jobs: list[JobPosting] = []

    for item in data.get("data", []):
        # Extract and validate required fields
        title = item.get("job_title", "").strip()
        company = item.get("employer_name", "").strip()
        url = item.get("job_apply_link") or item.get("job_google_link", "")
        date_posted = item.get("job_posted_at_datetime_utc", "")

        if not title or not company:
            continue

        # Normalize date to YYYY-MM-DD
        if date_posted:
            date_posted = date_posted[:10]  # trim time portion

        jobs.append(
            JobPosting(
                job_title=title,
                company=company,
                job_url=url,
                posting_date=date_posted,
                source="jsearch",
            )
        )

    logger.info("JSearch returned %d jobs for '%s'", len(jobs), query)
    return jobs


def _scrape_jobs(job_title: str, location: str) -> list[JobPosting]:
    """Playwright-based scraping fallback."""
    random_delay()
    # TODO: Implement real scraping with Playwright
    return []
