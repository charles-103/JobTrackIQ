from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.event import EventCreate, EventOut
from app.crud.crud_application import get_application
from app.crud.crud_event import add_event, list_events_for_application, delete_event

router = APIRouter(tags=["events"])


@router.post("/applications/{application_id}/events", response_model=EventOut)
def create_event(application_id: int, data: EventCreate, db: Session = Depends(get_db)):
    app_obj = get_application(db, application_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    try:
        return add_event(db, app_obj, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{application_id}/events", response_model=list[EventOut])
def list_events(
    application_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    app_obj = get_application(db, application_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    return list_events_for_application(db, application_id, limit=limit, offset=offset)


@router.delete("/events/{event_id}")
def delete_event_api(
    event_id: int,
    db: Session = Depends(get_db),
):
    ok = delete_event(db, event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"deleted": True}
