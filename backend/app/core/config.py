import os
from pathlib import Path
from dotenv import load_dotenv

# repo root = .../JobTrackIQ
REPO_ROOT = Path(__file__).resolve().parents[2]  # app/core/config.py -> app -> repo root
ENV_PATH = REPO_ROOT / ".env"

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is not set. Expected it in {ENV_PATH}")