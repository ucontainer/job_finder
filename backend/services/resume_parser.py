import json
from pathlib import Path

import anthropic
import pdfplumber

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import ResumeProfile

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

EXTRACTION_PROMPT = """Extract the following from the resume text below:

1. **job_title** — the primary (most recent or most relevant) job title.
2. **tech_stack** — a list of technologies, programming languages, frameworks, tools, and platforms mentioned (e.g., "Python", "AWS", "React", "Docker", "PostgreSQL"). Only include concrete technical skills, not soft skills.
3. **certifications** — a list of professional certifications mentioned (e.g., "AWS Solutions Architect", "PMP", "CISSP", "Google Cloud Professional"). Include the full certification name. If none are found, return an empty list.

Rules:
- Do NOT extract personal data (name, email, phone, address).
- If multiple job titles exist, pick the most recent one.
- For tech_stack, deduplicate and keep canonical names (e.g., "JS" → "JavaScript").
- Return ONLY a JSON object with this exact shape:

{"job_title": "...", "tech_stack": ["...", "..."], "certifications": ["...", "..."]}

Resume text:
"""


def extract_text_from_pdf(pdf_path: Path) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_resume_profile(resume_text: str) -> ResumeProfile:
    """Extract job title, tech stack, and certifications from resume text."""
    if not _client:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT + resume_text}
        ],
    )

    raw = message.content[0].text.strip()
    # Handle possible markdown code fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(raw)

    return ResumeProfile(
        job_title=data.get("job_title", "Unknown"),
        tech_stack=data.get("tech_stack", []),
        certifications=data.get("certifications", []),
    )
