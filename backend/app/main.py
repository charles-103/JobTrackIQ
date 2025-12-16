from fastapi import FastAPI

from app.core.database import test_db_connection
from app.api.v1 import all_routers

app = FastAPI(title="JobTrackIQ API")

# 如果你们 main 分支有 all_routers，就把路由挂上
for r in all_routers:
    app.include_router(r, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "JobTrackIQ API is running", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    ok = test_db_connection()
    return {"status": "ok", "db": "ok" if ok else "failed"}