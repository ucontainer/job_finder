# Jobbb Finder — AI Job-Matching Platform

## Layer 1: Directives (What & Why)

### Purpose
An AI-powered job-matching platform that extracts job titles from uploaded resumes (PDF), matches them against aggregated job postings using fuzzy matching, and generates personalized cover letters.

### Core Principles
- **Privacy-first**: Never extract or store personal data (name, email, phone) from resumes. Only extract the primary job title.
- **Relevance over volume**: Prioritize recent postings and high-similarity matches. Filter out clearly irrelevant roles.
- **Natural tone**: Cover letters must be conversational, concise (3–5 sentences), and free of placeholders like "[Your Name]".
- **No fabrication**: Never invent personal details, work history, or qualifications in cover letters.

### Constraints
- Resume parsing extracts **only** the primary job title (most recent/relevant if multiple exist).
- Job matching uses fuzzy matching — similar roles count (e.g., "Application Security Engineer" ≈ "Product Security Engineer").
- Sorting: **recency first**, then match score.
- Cover letters: light personalization (job title + company name), generic high-level skills only.
- Anti-ban: random delays, proxy rotation, rate limiting, caching. No aggressive crawling.

---

## Layer 2: Orchestration (How Things Connect)

### Data Flow
```
User Upload (PDF + Location)
        │
        ▼
┌─────────────────────┐
│  Resume Parser       │  ← pdfplumber / PyMuPDF
│  Extract text → LLM │  → { "job_title": "..." }
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Job Aggregator      │  ← APIs (LinkedIn, Indeed, ZipRecruiter)
│                      │  ← Scraping fallback (Playwright)
│  Filters: location,  │
│  date, relevance     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Matching Engine     │  ← rapidfuzz
│  Score: title sim +  │
│  recency weighting   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Cover Letter Gen    │  ← LLM (Claude API)
│  Per-job, batched    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Dashboard (React)   │  ← Job cards, cover letters, apply links
└─────────────────────┘
```

### API Contracts

**POST /api/upload**
- Input: PDF file + location string
- Output: `{ "job_title": "...", "session_id": "..." }`

**GET /api/jobs?session_id=...&sort=recency&min_score=70**
- Output: Array of matched jobs with cover letters (see output format below)

**Output schema per job:**
```json
{
  "job_title": "",
  "company": "",
  "job_url": "",
  "posting_date": "",
  "match_score": "",
  "cover_letter": ""
}
```

### Service Boundaries
| Service              | Responsibility                          | Key Dependency       |
|----------------------|-----------------------------------------|----------------------|
| Resume Parser        | PDF → text → job title                  | pdfplumber, LLM      |
| Job Aggregator       | Fetch postings by title + location      | APIs, Playwright     |
| Matching Engine      | Fuzzy score + sort                      | rapidfuzz            |
| Cover Letter Gen     | Generate per-job cover letters          | Claude API           |
| API Gateway (FastAPI)| Route requests, manage sessions         | FastAPI, Uvicorn     |
| Frontend             | Upload, filter, display results         | React                |

---

## Layer 3: Execution (How to Build & Run)

### Project Structure
```
jobbb_finder/
├── CLAUDE.md
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings, env vars
│   ├── services/
│   │   ├── resume_parser.py     # PDF extraction + LLM title extraction
│   │   ├── job_aggregator.py    # Job fetching (API + scraping)
│   │   ├── matching_engine.py   # Fuzzy matching + scoring
│   │   └── cover_letter.py     # LLM cover letter generation
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── routes/
│   │   └── api.py               # API route definitions
│   └── utils/
│       └── anti_ban.py          # Proxy rotation, delays, user agents
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── JobCard.jsx
│   │   │   ├── CoverLetterModal.jsx
│   │   │   └── Filters.jsx
│   │   └── api/
│   │       └── client.js
│   └── public/
│       └── index.html
├── requirements.txt
├── .env.example
└── .gitignore
```

### Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **PDF Parsing**: pdfplumber
- **Fuzzy Matching**: rapidfuzz
- **LLM**: Anthropic Claude API (resume parsing + cover letters)
- **Scraping**: Playwright (fallback only)
- **Frontend**: React 18, Vite
- **Styling**: Tailwind CSS

### Running Locally

**Backend:**
```bash
cd backend
pip install -r ../requirements.txt
cp ../.env.example ../.env   # fill in API keys
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```
ANTHROPIC_API_KEY=         # Required — Claude API
RAPIDAPI_KEY=              # Required — JSearch API via RapidAPI (free tier)
PROXY_LIST=                # Optional — comma-separated proxy URLs
SCRAPING_ENABLED=false     # Toggle scraping fallback
```

### Development Guidelines
- Run `ruff check backend/` before committing Python code.
- Keep services decoupled — each service file should be independently testable.
- All LLM calls go through the Claude API (anthropic SDK). Do not hardcode prompts in route handlers.
- Cache job results aggressively to reduce API/scraping load.
- Never commit `.env` or API keys.
