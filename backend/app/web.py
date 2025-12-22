from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_db
from app.crud.crud_application import (
    create_application,
    list_applications,
    get_application,
    update_application_status,
    delete_application
)

from app.crud.crud_event import (
    add_event,
    delete_event,
    list_events_for_application,
    latest_events_for_applications,
)
from app.models.event import Event
from app.crud.crud_metrics import metrics_overview, metrics_time_to_milestones, metrics_by_channel
from app.crud.crud_company import upsert_company_index
from app.schemas.application import ApplicationCreate
from app.schemas.event import EventCreate

from app.crud.crud_job_posting import create_job_posting, list_job_postings
from app.schemas.job_posting import JobPostingCreate
from app.crud.crud_company import upsert_company_index

from app.crud.crud_job_posting import get_job_posting, delete_job_posting

import urllib.parse

from app.ingest.greenhouse import fetch_greenhouse_jobs
from app.crud.crud_job_posting import upsert_job_posting  # 你之前加的通用 upsert
from app.crud.crud_company import upsert_company_index

import asyncio
from app.ingest.greenhouse import fetch_greenhouse_jobs, fetch_greenhouse_job_detail


templates = Jinja2Templates(directory="app/templates")


def _fmt_dt(dt):
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M")


templates.env.filters["dt"] = _fmt_dt
router = APIRouter(prefix="/ui")


@router.get("/")
def home(
    request: Request,
    search: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    # ✅ 默认值：无论 DB 是否可用/是否有数据，模板渲染都不会炸
    total, items = 0, []
    latest_events: dict[int, list] | dict = {}

    overview = {
        "total_applications": 0,
        "by_status": {},
        "offer_rate": 0.0,
        "rejection_rate": 0.0,
    }
    timing = {
        "avg_days_to_interview": None,
        "avg_days_to_offer": None,
    }
    channels = []
    db_error = None

    try:
        total, items = list_applications(
            db,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
            order_by="created_at",
            order="desc",
        )

        # 这些 metrics 在“空库 / 表不存在 / 连接失败”等情况下都可能抛 SQLAlchemyError
        overview = metrics_overview(db) or overview
        timing = metrics_time_to_milestones(db) or timing
        channels = metrics_by_channel(db, min_samples=1) or channels

        # items 为空时也别查
        if items:
            latest_events = latest_events_for_applications(db, [a.id for a in items])
        else:
            latest_events = {}
    except SQLAlchemyError as e:
        # ✅ 不让 UI 500，把错误显示到页面上
        db_error = str(e)

    # ✅ 用 .get 防止 metrics 返回缺 key 导致 KeyError
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "JobTrackIQ",
            "items": items,
            "total": total,
            "search": search,
            "status": status,
            "limit": limit,
            "offset": offset,
            "metrics_total": overview.get("total_applications", 0),
            "metrics_by_status": overview.get("by_status", {}),
            "offer_rate": overview.get("offer_rate", 0.0),
            "rejection_rate": overview.get("rejection_rate", 0.0),
            "avg_days_to_interview": timing.get("avg_days_to_interview"),
            "avg_days_to_offer": timing.get("avg_days_to_offer"),
            "channels": channels,
            "latest_events": latest_events,
            "db_error": db_error,
        },
        status_code=200,
    )


@router.post("/applications")
def create_app_form(
    company_name: str = Form(...),
    role_title: str = Form(...),
    channel: str | None = Form(None),
    location: str | None = Form(None),
    db: Session = Depends(get_db),
):
    obj = create_application(
        db,
        ApplicationCreate(
            company_name=company_name,
            role_title=role_title,
            channel=channel,
            location=location,
        ),
    )
    upsert_company_index(db, name=company_name, source="user_input")
    return RedirectResponse(url=f"/ui/applications/{obj.id}", status_code=303)

@router.post("/applications/{application_id}/delete", name="ui_application_delete")
def delete_application_ui(
    application_id: int,
    redirect_to: str | None = Form(None),
    db: Session = Depends(get_db),
):
    ok = delete_application(db, application_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Application not found")

    return RedirectResponse(url=(redirect_to or "/ui/"), status_code=303)

@router.post("/applications/{application_id}/status")
def update_status_form(
    application_id: int,
    status: str = Form(...),
    redirect_to: str | None = Form(None),
    db: Session = Depends(get_db),
):
    update_application_status(db, application_id, status)
    url = redirect_to or "/ui/"
    return RedirectResponse(url=url, status_code=303)


# ✅ 改动 1：支持 err 参数，把错误显示在详情页
@router.get("/applications/{application_id}")
def app_detail(
    request: Request,
    application_id: int,
    err: str | None = None,   # ✅ 新增
    db: Session = Depends(get_db),
):
    app_obj = get_application(db, application_id)
    if not app_obj:
        return RedirectResponse(url="/ui/", status_code=303)

    events = list_events_for_application(db, application_id, limit=200, offset=0)

    return templates.TemplateResponse(
        "application_detail.html",
        {
            "request": request,
            "title": f"Application {application_id}",
            "app": app_obj,
            "events": events,
            "err": err,  # ✅ 新增：模板可显示
        },
        status_code=200,
    )


# ✅ 改动 2：捕获 ValueError（强约束 FSM 触发时），避免 UI 500
@router.post("/applications/{application_id}/events")
def add_event_form(
    application_id: int,
    event_type: str = Form(...),
    notes: str | None = Form(None),
    db: Session = Depends(get_db),
):
    app_obj = get_application(db, application_id)
    if not app_obj:
        return RedirectResponse(url="/ui/", status_code=303)

    try:
        add_event(db, app_obj, EventCreate(event_type=event_type, notes=notes))
    except ValueError as e:
        # ✅ 回详情页并显示错误，不让用户看到 500
        # err 放 query string，简单可靠
        return RedirectResponse(url=f"/ui/applications/{application_id}?err={str(e)}", status_code=303)

    return RedirectResponse(url=f"/ui/applications/{application_id}", status_code=303)


@router.post("/events/{event_id}/delete", name="ui_event_delete")
def delete_event_ui(
    event_id: int,
    db: Session = Depends(get_db),
):
    obj = db.query(Event).filter(Event.id == event_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")

    app_id = obj.application_id

    ok = delete_event(db, event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")

    return RedirectResponse(url=f"/ui/applications/{app_id}", status_code=303)

@router.get("/jobs")
def jobs_page(
    request: Request,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    err: str | None = None,
    ok: str | None = None,
    db: Session = Depends(get_db),
):
    total, items = 0, []
    db_error = None

    try:
        total, items = list_job_postings(db, search=search, limit=limit, offset=offset)
    except SQLAlchemyError as e:
        db_error = str(e)

    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "title": "Job Inbox",
            "items": items,
            "total": total,
            "search": search,
            "limit": limit,
            "offset": offset,
            "err": err,
            "ok": ok,
            "db_error": db_error,
        },
        status_code=200,
    )

@router.post("/jobs")
def jobs_create(
    company_name: str = Form(...),
    role_title: str = Form(...),
    location: str | None = Form(None),
    url: str | None = Form(None),
    jd_text: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        obj = create_job_posting(
            db,
            JobPostingCreate(
                company_name=company_name,
                role_title=role_title,
                location=location,
                url=url,
                jd_text=jd_text,
            ),
        )
        # 反哺 company_index
        upsert_company_index(db, name=obj.company_name, source="manual")
    except Exception as e:
        return RedirectResponse(url=f"/ui/jobs?err={str(e)}", status_code=303)

    return RedirectResponse(url="/ui/jobs", status_code=303)

@router.post("/jobs/{job_id}/to-application", name="ui_job_to_application")
def job_to_application(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = get_job_posting(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # 1) 创建 application
    app_obj = create_application(
        db,
        ApplicationCreate(
            company_name=job.company_name,
            role_title=job.role_title,
            channel=job.source,      # 你也可以改成 "job_inbox"
            location=job.location,
        ),
    )

    # 2) 反哺 company index（保持共用系统）
    upsert_company_index(db, name=job.company_name, source="manual")

    # 3) 写一条 applied event（让 workflow 一致）
    try:
        add_event(db, app_obj, EventCreate(event_type="applied", notes=f"Created from Job Inbox (job_id={job.id})"))
    except ValueError:
        # applied 一般不会触发限制，保险起见
        pass

    # 4) 可选：转换后从 inbox 删除（推荐）
    delete_job_posting(db, job_id)

    # 跳转到详情页
    return RedirectResponse(url=f"/ui/applications/{app_obj.id}", status_code=303)

@router.post("/ingest/greenhouse", name="ui_ingest_greenhouse")
async def ui_ingest_greenhouse(
    board_token: str = Form(...),
    company_name: str = Form(...),
    fetch_jd: str | None = Form(None),  # ✅ checkbox: "on" or None
    db: Session = Depends(get_db),
):
    board_token = board_token.strip()
    company_name = company_name.strip()

    if not board_token or not company_name:
        return RedirectResponse(url="/ui/jobs?err=board_token%20and%20company_name%20required", status_code=303)

    try:
        jobs = await fetch_greenhouse_jobs(board_token)
    except Exception as e:
        msg = urllib.parse.quote(f"Greenhouse fetch failed: {e}")
        return RedirectResponse(url=f"/ui/jobs?err={msg}", status_code=303)

    # ✅ 是否抓 JD
    need_jd = (fetch_jd == "on")

    # ✅ 并发限制（别太猛）
    sem = asyncio.Semaphore(6)

    async def _get_jd(job_id: int) -> str | None:
        if not need_jd:
            return None
        async with sem:
            try:
                detail = await fetch_greenhouse_job_detail(board_token, job_id)
                # Greenhouse detail 常见字段：content (HTML), title, location...
                return detail.get("content")
            except Exception:
                return None

    # 先准备任务（仅对有 id 的 job）
    jd_map: dict[int, str | None] = {}
    if need_jd:
        tasks = []
        ids = []
        for j in jobs:
            job_id = j.get("id")
            if isinstance(job_id, int):
                ids.append(job_id)
                tasks.append(_get_jd(job_id))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for job_id, res in zip(ids, results):
            jd_map[job_id] = res if isinstance(res, str) else None

    upserted = 0
    for j in jobs:
        title = j.get("title") or ""
        if not title:
            continue
        location = (j.get("location") or {}).get("name")
        url = j.get("absolute_url")
        job_id = j.get("id")

        jd_text = None
        if need_jd and isinstance(job_id, int):
            jd_text = jd_map.get(job_id)

        obj = upsert_job_posting(
            db,
            source="greenhouse",
            company_name=company_name,
            role_title=title,
            location=location,
            url=url,
            jd_text=jd_text,  # ✅ 现在存入
        )
        upserted += 1
        upsert_company_index(db, name=obj.company_name, source="crawler")

    ok_msg = urllib.parse.quote(
        f"Imported {len(jobs)} jobs (upserted {upserted}) from {board_token}"
        + (" with JD" if need_jd else "")
    )
    return RedirectResponse(url=f"/ui/jobs?ok={ok_msg}", status_code=303)