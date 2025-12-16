from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from app.api.deps import get_db
from app.crud.crud_application import create_application, list_applications, get_application
from app.crud.crud_event import add_event, list_events_for_application
from app.schemas.application import ApplicationCreate
from app.schemas.event import EventCreate

templates = Jinja2Templates(directory="app/templates")
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
        db_error = None
    except SQLAlchemyError as e:
        # DB 连接/查询失败时：页面仍然返回，只是显示错误
        total, items = 0, []
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
            "db_error": db_error,
        },
        status_code=200 if db_error is None else 500,
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
    return RedirectResponse(url=f"/applications/{obj.id}", status_code=303)


@router.get("/applications/{application_id}")
def app_detail(
    request: Request,
    application_id: int,
    db: Session = Depends(get_db),
):
    app_obj = get_application(db, application_id)
    if not app_obj:
        return RedirectResponse(url="/", status_code=303)

    events = list_events_for_application(db, application_id, limit=200, offset=0)

    return templates.TemplateResponse(
        "application_detail.html",
        {
            "request": request,
            "title": f"Application {application_id}",
            "app": app_obj,
            "events": events,
        },
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
        return RedirectResponse(url="/", status_code=303)

    add_event(db, app_obj, EventCreate(event_type=event_type, notes=notes))
    return RedirectResponse(url=f"/applications/{application_id}", status_code=303)
