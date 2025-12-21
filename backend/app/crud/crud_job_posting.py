from __future__ import annotations

import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.job_posting import JobPosting
from app.schemas.job_posting import JobPostingCreate


def _norm(s: str | None) -> str:
    if not s:
        return ""
    return " ".join(s.strip().lower().split())


def build_fingerprint(*parts: str | None) -> str:
    raw = "|".join(_norm(p) for p in parts if p is not None)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_job_posting(db: Session, data: JobPostingCreate) -> JobPosting:
    fp = build_fingerprint(data.company_name, data.role_title, data.location, data.url)

    existing = db.query(JobPosting).filter(JobPosting.fingerprint == fp).first()
    if existing:
        # 已存在就直接返回（避免重复）
        return existing

    obj = JobPosting(
        source="manual",
        company_name=data.company_name.strip(),
        role_title=data.role_title.strip(),
        location=data.location.strip() if data.location else None,
        url=data.url.strip() if data.url else None,
        jd_text=data.jd_text.strip() if data.jd_text else None,
        fingerprint=fp,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_job_postings(
    db: Session,
    *,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[JobPosting]]:
    q = db.query(JobPosting)

    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            (JobPosting.company_name.ilike(s)) |
            (JobPosting.role_title.ilike(s)) |
            (JobPosting.location.ilike(s))
        )

    total = q.count()
    items = (
        q.order_by(desc(JobPosting.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return total, items
