from fastapi import FastAPI

from app.core.database import Base, engine
import app.models  # noqa: F401  确保模型被导入

from app.api.v1 import all_routers

app = FastAPI(title="JobTrackIQ API")

Base.metadata.create_all(bind=engine)

for r in all_routers:
    app.include_router(r, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"status": "ok"}
