"""Cover letter generation service — produces short, conversational letters via Claude."""

from __future__ import annotations

import anthropic

from backend.config import ANTHROPIC_API_KEY
from backend.models.schemas import MatchedJob, ResumeProfile

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

SYSTEM_PROMPT = """You generate short, conversational cover letter openings for job applications.
Rules:
- 3–5 sentences maximum.
- Mention the job title and company name.
- Use a natural, friendly tone — not overly formal.
- Focus on alignment with the role, interest in the company, and relevant high-level skills.
- You may reference specific technologies or certifications from the candidate's profile when they are relevant to the role, but keep it brief.
- Do NOT fabricate personal details or work history.
- Do NOT include placeholders like [Your Name] or [Company].
- Do NOT include a greeting or sign-off — just the body paragraph."""


def generate_cover_letter(job: MatchedJob, profile: ResumeProfile) -> str:
    tech_str = ", ".join(profile.tech_stack[:8]) if profile.tech_stack else "various technologies"
    cert_str = ", ".join(profile.certifications[:4]) if profile.certifications else ""

    if not _client:
        parts = [
            f"I'm excited about the {job.job_title} role at {job.company}. ",
            f"With my background as a {profile.job_title} and experience with {tech_str}, ",
            f"I believe I can contribute meaningfully to your team. ",
        ]
        if cert_str:
            parts.append(f"My certifications ({cert_str}) further demonstrate my commitment to the field. ")
        parts.append("I'd love the opportunity to discuss how my skills align with your needs.")
        return "".join(parts)

    user_content = (
        f"Write a cover letter body for this job:\n"
        f"- Position: {job.job_title}\n"
        f"- Company: {job.company}\n"
        f"- My current/recent title: {profile.job_title}\n"
        f"- My tech stack: {tech_str}\n"
    )
    if cert_str:
        user_content += f"- My certifications: {cert_str}\n"

    message = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text.strip()


def generate_cover_letters_batch(
    jobs: list[MatchedJob], profile: ResumeProfile
) -> list[MatchedJob]:
    """Generate cover letters for a list of matched jobs. Mutates and returns the list."""
    for job in jobs:
        job.cover_letter = generate_cover_letter(job, profile)
    return jobs
