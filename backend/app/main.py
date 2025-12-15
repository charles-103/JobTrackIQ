from fastapi import FastAPI
from app.core.database import test_db_connection

app = FastAPI(title="JobTrackIQ API")


@app.get("/")
def root():
    return {"message": "JobTrackIQ API is running", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    ok = test_db_connection()
    return {"status": "ok", "db": "ok" if ok else "failed"}