"""API routes for the job-matching platform."""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.config import UPLOAD_DIR
from backend.models.schemas import MatchedJob, ResumeProfile, UploadResponse
from backend.services.cover_letter import generate_cover_letters_batch
from backend.services.job_aggregator import fetch_jobs
from backend.services.matching_engine import match_jobs
from backend.services.resume_parser import extract_resume_profile, extract_text_from_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# ---------- Session persistence ----------
# File-based session store so sessions survive server restarts.
# For multi-instance deployments, replace with Redis or a database.

_SESSIONS_FILE = UPLOAD_DIR / "_sessions.json"


def _load_sessions() -> dict[str, dict]:
    if _SESSIONS_FILE.exists():
        try:
            return json.loads(_SESSIONS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_session(session_id: str, profile: ResumeProfile) -> None:
    sessions = _load_sessions()
    sessions[session_id] = profile.model_dump()
    try:
        _SESSIONS_FILE.write_text(json.dumps(sessions))
    except OSError as exc:
        logger.warning("Could not persist session: %s", exc)


def _get_session(session_id: str) -> ResumeProfile | None:
    sessions = _load_sessions()
    data = sessions.get(session_id)
    if data:
        return ResumeProfile(**data)
    return None


# ---------- Routes ----------


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    location: str = Form(""),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    session_id = uuid.uuid4().hex
    pdf_path = UPLOAD_DIR / f"{session_id}.pdf"

    content = await file.read()
    pdf_path.write_bytes(content)

    try:
        text = extract_text_from_pdf(pdf_path)
        profile = extract_resume_profile(text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse resume: {exc}")
    finally:
        pdf_path.unlink(missing_ok=True)

    _save_session(session_id, profile)
    return UploadResponse(
        job_title=profile.job_title,
        tech_stack=profile.tech_stack,
        certifications=profile.certifications,
        session_id=session_id,
    )


@router.get("/jobs", response_model=list[MatchedJob])
async def get_matched_jobs(
    session_id: str,
    location: str = "",
    min_score: float = 40.0,
):
    profile = _get_session(session_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Session not found. Upload a resume first.")

    postings = fetch_jobs(profile.job_title, location)
    matched = match_jobs(profile.job_title, postings, min_score=min_score)
    matched = generate_cover_letters_batch(matched, profile)
    return matched
