# Jobbb Finder

AI-powered job-matching platform that extracts your job title from a resume, finds relevant postings, and generates cover letters.

## Prerequisites

- Python 3.11+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)
- A [RapidAPI key](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) (free tier — 200 requests/month)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ucontainer/job_finder.git
cd job_finder
```

### 2. Configure environment variables

```bash
# Linux / Mac
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` and add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
RAPIDAPI_KEY=your-rapidapi-key
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

## Running the Application

Start both the backend and frontend in separate terminals:

**Backend** (from project root):

```bash
uvicorn backend.main:app --reload --port 8000
```

**Frontend** (from `frontend/`):

```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

## Usage

1. Open the dashboard in your browser.
2. Upload a PDF resume using the file picker.
3. Optionally enter a location (e.g., "Berlin", "Remote").
4. Click **Find Jobs** — the app will:
   - Extract your primary job title from the resume
   - Fetch and rank matching job postings
   - Generate a short cover letter for each match
5. Browse job cards sorted by match score.
6. Click **View Cover Letter** to see and copy the generated letter.
7. Click **Apply** to open the job posting in a new tab.

## API Endpoints

| Method | Endpoint       | Description                          |
|--------|----------------|--------------------------------------|
| POST   | `/api/upload`  | Upload PDF + location, returns extracted job title and session ID |
| GET    | `/api/jobs`    | Fetch matched jobs with cover letters (requires `session_id` query param) |
| GET    | `/health`      | Health check                         |

## Project Structure

```
job_finder/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Environment config
│   ├── services/
│   │   ├── resume_parser.py     # PDF → job title extraction
│   │   ├── job_aggregator.py    # Job fetching + caching
│   │   ├── matching_engine.py   # Fuzzy matching (rapidfuzz)
│   │   └── cover_letter.py      # Cover letter generation
│   ├── models/schemas.py        # Pydantic models
│   ├── routes/api.py            # API routes
│   └── utils/anti_ban.py        # Scraping utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   ├── components/          # UI components
│   │   └── api/client.js        # API client
│   └── index.html
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

## Deployment

The app is deployment-ready for platforms like **Render**, **Railway**, or **Heroku**.

### Render (recommended)

A `render.yaml` is included for one-click deploy:

1. Push the repo to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
3. Connect the repo — Render will auto-detect `render.yaml`.
4. Set the environment variables in the Render dashboard:
   - `ANTHROPIC_API_KEY`
   - `RAPIDAPI_KEY`
   - `FRONTEND_URL` → your frontend's Render URL (e.g., `https://jobbb-finder-frontend.onrender.com`)
   - `VITE_API_URL` → your backend's Render URL + `/api` (e.g., `https://jobbb-finder-api.onrender.com/api`)

### Other platforms

Use the included `Procfile`:

```bash
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

For the frontend, build with `VITE_API_URL` pointing to your backend:

```bash
cd frontend
VITE_API_URL=https://your-backend-url.com/api npm run build
```

Then serve the `frontend/dist/` folder as a static site.

### Environment variables for production

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `RAPIDAPI_KEY` | Yes | JSearch API key (RapidAPI) |
| `FRONTEND_URL` | Yes | Frontend URL for CORS (e.g., `https://your-app.com`) |
| `VITE_API_URL` | Yes | Backend API URL for frontend (e.g., `https://api.your-app.com/api`) |
| `PORT` | Auto | Set automatically by hosting platforms |

## Notes

- Set `SCRAPING_ENABLED=true` in `.env` to enable the Playwright scraping fallback.
- Job results are cached for 1 hour to reduce API load.
- Sessions are persisted to a JSON file — for multi-instance scaling, replace with Redis or a database.
