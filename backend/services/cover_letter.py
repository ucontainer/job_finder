"""Cover letter and motivation generation service via Claude."""

from __future__ import annotations

import json

import anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import MatchedJob, ResumeProfile

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

SYSTEM_PROMPT = """You generate two things for a job application:

1. A short, conversational cover letter opening (3–5 sentences).
2. Two concise reasons why this candidate would want to work at this company as the given role.

Rules for the cover letter:
- Mention the job title and company name.
- Use a natural, friendly tone — not overly formal.
- Focus on alignment with the role, interest in the company, and relevant high-level skills.
- You may reference specific technologies or certifications from the candidate's profile when relevant, but keep it brief.
- Do NOT fabricate personal details or work history.
- Do NOT include placeholders like [Your Name] or [Company].
- Do NOT include a greeting or sign-off — just the body paragraph.

Rules for the "why work here" reasons:
- Exactly 2 reasons, each 1 sentence.
- Write from the candidate's perspective as a professional with their job title.
- Natural, conversational tone — not generic or corporate-speak.
- Relate each reason to how the role aligns with their skills or career growth.
- Do NOT fabricate specifics about the company you don't know.

Return ONLY a JSON object with this exact shape:
{"cover_letter": "...", "why_work_here": "1) ... 2) ..."}"""


def generate_cover_letter_and_reasons(job: MatchedJob, profile: ResumeProfile) -> tuple[str, str]:
    tech_str = ", ".join(profile.tech_stack[:8]) if profile.tech_stack else "various technologies"
    cert_str = ", ".join(profile.certifications[:4]) if profile.certifications else ""

    if not _client:
        cover_letter = (
            f"I'm excited about the {job.job_title} role at {job.company}. "
            f"With my background as a {profile.job_title} and experience with {tech_str}, "
            f"I believe I can contribute meaningfully to your team. "
        )
        if cert_str:
            cover_letter += f"My certifications ({cert_str}) further demonstrate my commitment to the field. "
        cover_letter += "I'd love the opportunity to discuss how my skills align with your needs."

        why_work_here = (
            f"1) The {job.job_title} role is a strong fit for my {profile.job_title} background "
            f"and would let me apply my experience with {tech_str} in a meaningful way. "
            f"2) Working at {job.company} would offer a great opportunity to grow professionally "
            f"while contributing to impactful projects."
        )
        return cover_letter, why_work_here

    user_content = (
        f"Generate a cover letter and two reasons to work here:\n"
        f"- Position: {job.job_title}\n"
        f"- Company: {job.company}\n"
        f"- My current/recent title: {profile.job_title}\n"
        f"- My tech stack: {tech_str}\n"
    )
    if cert_str:
        user_content += f"- My certifications: {cert_str}\n"

    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        data = json.loads(raw)
        return data.get("cover_letter", ""), data.get("why_work_here", "")
    except (json.JSONDecodeError, AttributeError):
        return raw, ""


def generate_cover_letters_batch(
    jobs: list[MatchedJob], profile: ResumeProfile
) -> list[MatchedJob]:
    """Generate cover letters and reasons for a list of matched jobs."""
    for job in jobs:
        job.cover_letter, job.why_work_here = generate_cover_letter_and_reasons(job, profile)
    return jobs
