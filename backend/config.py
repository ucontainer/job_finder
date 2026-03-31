import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
PROXY_LIST = [p.strip() for p in os.getenv("PROXY_LIST", "").split(",") if p.strip()]
SCRAPING_ENABLED = os.getenv("SCRAPING_ENABLED", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))

# Use temp dir for uploads — safe on ephemeral filesystems (Render, Railway, etc.)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", tempfile.gettempdir())) / "jobbb_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
