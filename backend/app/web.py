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
from app.crud.crud_event import add_event, delete_event, list_events_for_application, latest_events_for_applications
from app.models.event import Event
from app.crud.crud_metrics import metrics_overview
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
    # ✅ 永远给默认值，避免 except 时变量未定义
    total, items = 0, []
    latest_events = {}
    overview = {"total_applications": 0, "by_status": {}}
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
        overview = metrics_overview(db)
        latest_events = latest_events_for_applications(db, [a.id for a in items])
    except SQLAlchemyError as e:
        db_error = str(e)

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
            "metrics_total": overview["total_applications"],
            "metrics_by_status": overview["by_status"],
            "latest_events": latest_events,
            "db_error": db_error,
        },
        # ✅ UI 页面建议一直 200，把错误显示在页面上即可
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
    # ✅ 注意 /ui 前缀
    return RedirectResponse(url=f"/ui/applications/{obj.id}", status_code=303)


@router.post("/applications/{application_id}/status")
def update_status_form(
    application_id: int,
    status: str = Form(...),
    redirect_to: str | None = Form(None),
    db: Session = Depends(get_db),
):
    update_application_status(db, application_id, status)

    # ✅ 回到原页面（保留搜索/分页）
    url = redirect_to or "/ui/"
    return RedirectResponse(url=url, status_code=303)


@router.get("/applications/{application_id}")
def app_detail(
    request: Request,
    application_id: int,
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
        },
        status_code=200,
    )


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

    add_event(db, app_obj, EventCreate(event_type=event_type, notes=notes))
    # ✅ 注意 /ui 前缀
    return RedirectResponse(url=f"/ui/applications/{application_id}", status_code=303)

@router.post("/events/{event_id}/delete", name="ui_event_delete")
def delete_event_ui(
    event_id: int,
    db: Session = Depends(get_db),
):
    # 先查出 application_id，保证删完能跳回正确详情页
    obj = db.query(Event).filter(Event.id == event_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")

    app_id = obj.application_id

    ok = delete_event(db, event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")

    return RedirectResponse(url=f"/ui/applications/{app_id}", status_code=303)