from pydantic import BaseModel


class ResumeProfile(BaseModel):
    job_title: str
    tech_stack: list[str] = []
    certifications: list[str] = []


class UploadResponse(BaseModel):
    job_title: str
    tech_stack: list[str] = []
    certifications: list[str] = []
    session_id: str


class JobPosting(BaseModel):
    job_title: str
    company: str
    job_url: str
    posting_date: str
    source: str = ""


class MatchedJob(BaseModel):
    job_title: str
    company: str
    job_url: str
    posting_date: str
    match_score: float
    cover_letter: str = ""
