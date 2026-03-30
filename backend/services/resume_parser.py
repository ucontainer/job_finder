from pathlib import Path

import anthropic
import pdfplumber

from backend.config import ANTHROPIC_API_KEY

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

EXTRACTION_PROMPT = """Extract the primary job title from the following resume text.
Rules:
- Only return the most recent or most relevant job title.
- Do NOT extract personal data (name, email, phone, address).
- If multiple titles exist, pick the most recent one.
- Return ONLY a JSON object: {"job_title": "<title>"}

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


def extract_job_title(resume_text: str) -> str:
    if not _client:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT + resume_text}
        ],
    )
    import json

    raw = message.content[0].text.strip()
    # Handle possible markdown code fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data = json.loads(raw)
    return data["job_title"]
