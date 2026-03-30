"""API routes for the job-matching platform."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.config import UPLOAD_DIR
from backend.models.schemas import MatchedJob, UploadResponse
from backend.services.cover_letter import generate_cover_letters_batch
from backend.services.job_aggregator import fetch_jobs
from backend.services.matching_engine import match_jobs
from backend.services.resume_parser import extract_job_title, extract_text_from_pdf

router = APIRouter(prefix="/api")

# In-memory session store: session_id → job_title
_sessions: dict[str, str] = {}


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
        job_title = extract_job_title(text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse resume: {exc}")
    finally:
        pdf_path.unlink(missing_ok=True)

    _sessions[session_id] = job_title
    return UploadResponse(job_title=job_title, session_id=session_id)


@router.get("/jobs", response_model=list[MatchedJob])
async def get_matched_jobs(
    session_id: str,
    location: str = "",
    min_score: float = 40.0,
):
    job_title = _sessions.get(session_id)
    if not job_title:
        raise HTTPException(status_code=404, detail="Session not found. Upload a resume first.")

    postings = fetch_jobs(job_title, location)
    matched = match_jobs(job_title, postings, min_score=min_score)
    matched = generate_cover_letters_batch(matched, job_title)
    return matched
