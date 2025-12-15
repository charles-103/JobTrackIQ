from fastapi import FastAPI
from app.core.database import test_db_connection

app = FastAPI(title="JobTrackIQ API")

@app.get("/health")
def health():
    # Basic app health check + DB connectivity check
    ok = test_db_connection()
    return {"status": "ok", "db": "ok" if ok else "failed"}

@app.get("/")
def root():
    return {"message": "JobTrackIQ API is running", "docs": "/docs", "health": "/health"}

