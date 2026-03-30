"""Job aggregation service — fetches postings from APIs and optional scraping fallback."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timedelta

from backend.config import SCRAPING_ENABLED
from backend.models.schemas import JobPosting
from backend.utils.anti_ban import random_delay

# In-memory cache: key → (timestamp, results)
_cache: dict[str, tuple[float, list[JobPosting]]] = {}
CACHE_TTL = 3600  # 1 hour


def _cache_key(job_title: str, location: str) -> str:
    return hashlib.sha256(f"{job_title.lower()}|{location.lower()}".encode()).hexdigest()


def fetch_jobs(job_title: str, location: str) -> list[JobPosting]:
    """Fetch job postings for a given title and location.

    Tries API sources first, falls back to scraping if enabled.
    Results are cached for CACHE_TTL seconds.
    """
    key = _cache_key(job_title, location)
    if key in _cache:
        ts, cached = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return cached

    jobs: list[JobPosting] = []

    # --- API sources (stub — replace with real integrations) ---
    jobs.extend(_fetch_from_apis(job_title, location))

    # --- Scraping fallback ---
    if not jobs and SCRAPING_ENABLED:
        jobs.extend(_scrape_jobs(job_title, location))

    # If no real sources available yet, return demo data
    if not jobs:
        jobs = _demo_jobs(job_title, location)

    _cache[key] = (time.time(), jobs)
    return jobs


def _fetch_from_apis(job_title: str, location: str) -> list[JobPosting]:
    """Placeholder for real API integrations (LinkedIn, Indeed, ZipRecruiter)."""
    # TODO: Integrate real job board APIs
    return []


def _scrape_jobs(job_title: str, location: str) -> list[JobPosting]:
    """Playwright-based scraping fallback."""
    random_delay()
    # TODO: Implement real scraping with Playwright
    return []


def _demo_jobs(job_title: str, location: str) -> list[JobPosting]:
    """Return sample data so the UI works before real integrations are wired up."""
    today = datetime.now()
    return [
        JobPosting(
            job_title=job_title,
            company="Acme Corp",
            job_url="https://example.com/jobs/1",
            posting_date=(today - timedelta(days=1)).strftime("%Y-%m-%d"),
            source="demo",
        ),
        JobPosting(
            job_title=f"Senior {job_title}",
            company="Globex Inc",
            job_url="https://example.com/jobs/2",
            posting_date=(today - timedelta(days=3)).strftime("%Y-%m-%d"),
            source="demo",
        ),
        JobPosting(
            job_title=f"{job_title} Lead",
            company="Initech",
            job_url="https://example.com/jobs/3",
            posting_date=(today - timedelta(days=7)).strftime("%Y-%m-%d"),
            source="demo",
        ),
        JobPosting(
            job_title=f"Junior {job_title}",
            company="Umbrella Corp",
            job_url="https://example.com/jobs/4",
            posting_date=(today - timedelta(days=14)).strftime("%Y-%m-%d"),
            source="demo",
        ),
    ]
