from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.job_posting import JobPostingCreate, JobPostingOut
from app.crud.crud_job_posting import create_job_posting, list_job_postings
from app.crud.crud_company import upsert_company_index

router = APIRouter(tags=["jobs"])


@router.post("/jobs", response_model=JobPostingOut)
def create_job(data: JobPostingCreate, db: Session = Depends(get_db)):
    obj = create_job_posting(db, data)
    # 反哺公司索引（非常关键：共用系统）
    upsert_company_index(db, name=obj.company_name, source="manual")
    return obj


@router.get("/jobs", response_model=list[JobPostingOut])
def list_jobs(
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    _, items = list_job_postings(db, search=search, limit=limit, offset=offset)
    return items
