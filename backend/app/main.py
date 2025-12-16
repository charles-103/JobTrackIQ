from fastapi import FastAPI

from app.core.database import test_db_connection
from app.api.v1 import all_routers
from app.web import router as web_router

app = FastAPI(title="JobTrackIQ API")

# API 路由
for r in all_routers:
    app.include_router(r, prefix="/api/v1")

# Web UI（Jinja2）
app.include_router(web_router)


@app.get("/health")
def health():
    ok = test_db_connection()
    return {"status": "ok", "db": "ok" if ok else "failed"}
