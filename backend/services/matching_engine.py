"""Fuzzy matching engine — scores and sorts job postings by relevance."""

from __future__ import annotations

from datetime import datetime

from rapidfuzz import fuzz

from backend.models.schemas import JobPosting, MatchedJob

# Weights for final score
TITLE_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3
RECENCY_HALF_LIFE_DAYS = 14  # postings lose half their recency score after this many days


def _title_similarity(user_title: str, job_title: str) -> float:
    """Return 0–100 similarity score using token-set ratio for fuzzy matching."""
    return fuzz.token_set_ratio(user_title.lower(), job_title.lower())


def _recency_score(posting_date: str) -> float:
    """Return 0–100 score based on how recent the posting is."""
    try:
        posted = datetime.strptime(posting_date, "%Y-%m-%d")
    except ValueError:
        return 0.0
    days_old = max((datetime.now() - posted).days, 0)
    # Exponential decay
    return 100.0 * (0.5 ** (days_old / RECENCY_HALF_LIFE_DAYS))


def match_jobs(
    user_title: str,
    postings: list[JobPosting],
    min_score: float = 40.0,
) -> list[MatchedJob]:
    """Score, filter, and sort job postings against the user's title."""
    results: list[MatchedJob] = []

    for posting in postings:
        title_sim = _title_similarity(user_title, posting.job_title)
        recency = _recency_score(posting.posting_date)
        combined = (TITLE_WEIGHT * title_sim) + (RECENCY_WEIGHT * recency)

        if combined < min_score:
            continue

        results.append(
            MatchedJob(
                job_title=posting.job_title,
                company=posting.company,
                job_url=posting.job_url,
                posting_date=posting.posting_date,
                match_score=round(combined, 1),
            )
        )

    # Sort: highest score first
    results.sort(key=lambda j: j.match_score, reverse=True)
    return results
