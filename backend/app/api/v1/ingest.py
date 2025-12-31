from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.ingest.greenhouse import fetch_greenhouse_jobs
from app.ingest.lever import fetch_lever_jobs
from app.ingest.smartrecruiters import fetch_smartrecruiters_jobs
from app.ingest.workday import fetch_workday_jobs
from app.crud.crud_job_posting import upsert_job_posting
from app.crud.crud_company import upsert_company_index

router = APIRouter(tags=["ingest"])


@router.post("/ingest/greenhouse/{board_token}")
async def ingest_greenhouse(
    board_token: str,
    company_name: str = Query(None),
    db: Session = Depends(get_db)
):
    try:
        jobs = await fetch_greenhouse_jobs(board_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Greenhouse fetch failed: {e}")

    created_or_existing = 0
    company_name = company_name or board_token

    for j in jobs:
        title = j.get("title") or ""
        location = (j.get("location") or {}).get("name")
        url = j.get("absolute_url")

        if not title:
            continue

        obj = upsert_job_posting(
            db,
            source="greenhouse",
            company_name=company_name,
            role_title=title,
            location=location,
            url=url,
            jd_text=None,
        )
        created_or_existing += 1
        upsert_company_index(db, name=obj.company_name, source="crawler")

    return {"board": board_token, "fetched": len(jobs), "upserted": created_or_existing}


@router.post("/ingest/lever/{site}")
async def ingest_lever(
    site: str,
    company_name: str = Query(None),
    db: Session = Depends(get_db)
):
    try:
        jobs = await fetch_lever_jobs(site)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lever fetch failed: {e}")

    created_or_existing = 0
    company_name = company_name or site

    for j in jobs:
        title = j.get("text") or j.get("title") or ""
        location = j.get("categories", {}).get("location") if isinstance(j.get("categories"), dict) else None
        url = j.get("hostedUrl") or j.get("applyUrl")

        if not title:
            continue

        obj = upsert_job_posting(
            db,
            source="lever",
            company_name=company_name,
            role_title=title,
            location=location,
            url=url,
            jd_text=j.get("descriptionPlain") or j.get("description"),
        )
        created_or_existing += 1
        upsert_company_index(db, name=obj.company_name, source="crawler")

    return {"site": site, "fetched": len(jobs), "upserted": created_or_existing}


@router.post("/ingest/smartrecruiters/{company_identifier}")
async def ingest_smartrecruiters(
    company_identifier: str,
    company_name: str = Query(None),
    db: Session = Depends(get_db)
):
    try:
        jobs = await fetch_smartrecruiters_jobs(company_identifier)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SmartRecruiters fetch failed: {e}")

    created_or_existing = 0
    company_name = company_name or company_identifier

    for j in jobs:
        title = j.get("name") or j.get("title") or ""
        location = j.get("location", {}).get("city") if isinstance(j.get("location"), dict) else None
        url = j.get("ref") or j.get("url")

        if not title:
            continue

        obj = upsert_job_posting(
            db,
            source="smartrecruiters",
            company_name=company_name,
            role_title=title,
            location=location,
            url=url,
            jd_text=j.get("jobAd", {}).get("sections", {}).get("jobDescription", {}).get("text") if isinstance(j.get("jobAd"), dict) else None,
        )
        created_or_existing += 1
        upsert_company_index(db, name=obj.company_name, source="crawler")

    return {"company": company_identifier, "fetched": len(jobs), "upserted": created_or_existing}


@router.post("/ingest/workday")
async def ingest_workday(
    careers_site_url: str = Query(...),
    company_name: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        jobs = await fetch_workday_jobs(careers_site_url, company_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Workday fetch failed: {e}")

    created_or_existing = 0

    for j in jobs:
        title = j.get("title") or ""
        location = j.get("location")
        url = j.get("url")

        if not title:
            continue

        obj = upsert_job_posting(
            db,
            source="workday",
            company_name=company_name,
            role_title=title,
            location=location,
            url=url,
            jd_text=None,
        )
        created_or_existing += 1
        upsert_company_index(db, name=obj.company_name, source="crawler")

    return {"url": careers_site_url, "fetched": len(jobs), "upserted": created_or_existing}
