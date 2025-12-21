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
