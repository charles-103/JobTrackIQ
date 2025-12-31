from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.job_posting import JobPostingCreate, JobPostingOut, JobPostingList
from app.schemas.application import ApplicationCreate, ApplicationOut
from app.crud.crud_job_posting import create_job_posting, list_job_postings, get_job_posting, delete_job_posting
from app.crud.crud_application import create_application
from app.crud.crud_event import add_event
from app.crud.crud_company import upsert_company_index
from app.schemas.event import EventCreate

router = APIRouter(tags=["jobs"])


@router.post("/jobs", response_model=JobPostingOut)
def create_job(data: JobPostingCreate, db: Session = Depends(get_db)):
    obj = create_job_posting(db, data)
    # 反哺公司索引（非常关键：共用系统�?
    upsert_company_index(db, name=obj.company_name, source="manual")
    return obj


@router.get("/jobs", response_model=JobPostingList)
def list_jobs(
    search: str | None = None,
    location: str | None = None,
    skills: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, items = list_job_postings(
        db, 
        search=search, 
        location=location,
        skills=skills,
        limit=limit, 
        offset=offset
    )
    return {"total": total, "items": items}


@router.post("/jobs/{job_id}/to-application", response_model=ApplicationOut)
def job_to_application_api(
    job_id: int,
    db: Session = Depends(get_db),
):
    """Convert a job posting to an application"""
    job = get_job_posting(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Create application
    app_obj = create_application(
        db,
        ApplicationCreate(
            company_name=job.company_name,
            role_title=job.role_title,
            channel=job.source or "job_inbox",
            location=job.location,
        ),
    )

    # Update company index
    upsert_company_index(db, name=job.company_name, source="manual")

    # Add applied event
    try:
        add_event(
            db,
            app_obj,
            EventCreate(event_type="applied", notes=f"Created from Job Inbox (job_id={job.id})")
        )
    except ValueError:
        # Applied event usually doesn't trigger restrictions
        pass

    # Delete the job posting after conversion
    delete_job_posting(db, job_id)

    return app_obj

