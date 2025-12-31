from __future__ import annotations

import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, any_

from app.models.job_posting import JobPosting
from app.schemas.job_posting import JobPostingCreate
from app.services.jd_parser import process_jd



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

    # 处理JD文本
    jd_data = process_jd(data.jd_text) if data.jd_text else {"processed_jd": None, "key_skills": None, "summary": None}

    obj = JobPosting(
        source="manual",
        company_name=data.company_name.strip(),
        role_title=data.role_title.strip(),
        location=data.location.strip() if data.location else None,
        url=data.url.strip() if data.url else None,
        jd_text=data.jd_text.strip() if data.jd_text else None,
        processed_jd=jd_data.get("processed_jd"),
        key_skills=jd_data.get("key_skills"),
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
    location: str | None = None,
    skills: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[JobPosting]]:
    q = db.query(JobPosting)

    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            (JobPosting.company_name.ilike(s)) |
            (JobPosting.role_title.ilike(s)) |
            (JobPosting.location.ilike(s)) |
            (JobPosting.processed_jd.ilike(s))
        )
    
    # 按地区筛选
    if location:
        loc = f"%{location.strip()}%"
        q = q.filter(JobPosting.location.ilike(loc))
    
    # 按技能筛选
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(',')]
        # 使用PostgreSQL的数组操作符 @> (包含) 或 && (重叠)
        from sqlalchemy import func
        conditions = []
        for skill in skill_list:
            # 使用数组重叠操作符 && 来检查是否有匹配的技能
            # 或者使用字符串匹配
            conditions.append(
                func.array_to_string(JobPosting.key_skills, ',').ilike(f"%{skill}%")
            )
        if conditions:
            q = q.filter(or_(*conditions))

    total = q.count()
    items = (
        q.order_by(desc(JobPosting.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return total, items

def get_job_posting(db: Session, job_id: int) -> JobPosting | None:
    return db.query(JobPosting).filter(JobPosting.id == job_id).first()

def delete_job_posting(db: Session, job_id: int) -> bool:
    obj = get_job_posting(db, job_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def upsert_job_posting(
    db: Session,
    *,
    source: str,
    company_name: str,
    role_title: str,
    location: str | None = None,
    url: str | None = None,
    jd_text: str | None = None,
) -> JobPosting:
    fp = build_fingerprint(company_name, role_title, location, url)

    existing = db.query(JobPosting).filter(JobPosting.fingerprint == fp).first()
    if existing:
        # 如果已有JD但需要更新，更新处理后的JD和技能
        if jd_text and (not existing.processed_jd or existing.jd_text != jd_text):
            jd_data = process_jd(jd_text)
            existing.jd_text = jd_text.strip()
            existing.processed_jd = jd_data.get("processed_jd")
            existing.key_skills = jd_data.get("key_skills")
            db.commit()
            db.refresh(existing)
        return existing

    # 处理JD文本
    jd_data = process_jd(jd_text) if jd_text else {"processed_jd": None, "key_skills": None, "summary": None}

    obj = JobPosting(
        source=source,
        company_name=company_name.strip(),
        role_title=role_title.strip(),
        location=location.strip() if location else None,
        url=url.strip() if url else None,
        jd_text=jd_text.strip() if jd_text else None,
        processed_jd=jd_data.get("processed_jd"),
        key_skills=jd_data.get("key_skills"),
        fingerprint=fp,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
