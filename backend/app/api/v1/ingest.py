from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.ingest.greenhouse import fetch_greenhouse_jobs
from app.crud.crud_job_posting import upsert_job_posting
from app.crud.crud_company import upsert_company_index

router = APIRouter(tags=["ingest"])


@router.post("/ingest/greenhouse/{board_token}")
async def ingest_greenhouse(board_token: str, db: Session = Depends(get_db)):
    try:
        jobs = await fetch_greenhouse_jobs(board_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Greenhouse fetch failed: {e}")

    created_or_existing = 0

    for j in jobs:
        # Greenhouse jobs fields (common):
        # id, title, location: {name}, absolute_url, updated_at
        title = j.get("title") or ""
        location = (j.get("location") or {}).get("name")
        url = j.get("absolute_url")

        # company_name：Greenhouse API 不一定直接给公司名
        # MVP：先用 board_token 当 company（或你可传 query 参数 company=xxx）
        company_name = board_token

        if not title:
            continue

        obj = upsert_job_posting(
            db,
            source="greenhouse",
            company_name=company_name,
            role_title=title,
            location=location,
            url=url,
            jd_text=None,  # 列表接口通常没有完整JD，下一步可抓详情页
        )
        created_or_existing += 1

        # 反哺公司索引（共用系统）
        upsert_company_index(db, name=obj.company_name, source="crawler")

    return {"board": board_token, "fetched": len(jobs), "upserted": created_or_existing}
