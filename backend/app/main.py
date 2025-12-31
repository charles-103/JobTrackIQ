from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import test_db_connection
from app.api.v1 import all_routers
from app.web import router as web_router

# 临时DB
import app.models
from app.core.database import Base, engine

app = FastAPI(title="JobTrackIQ API")

# CORS 配置 - 允许 React 前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite 默认端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
for r in all_routers:
    app.include_router(r, prefix="/api/v1")

# Web UI（Jinja2）
app.include_router(web_router)


@app.get("/health")
def health():
    ok = test_db_connection()
    return {"status": "ok", "db": "ok" if ok else "failed"}

from app.core.database import Base, engine

#Base.metadata.create_all(bind=engine)

