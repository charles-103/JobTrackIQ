from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.event import EventCreate, EventOut
from app.crud.crud_application import get_application
from app.crud.crud_event import add_event

router = APIRouter(tags=["events"])


@router.post("/applications/{application_id}/events", response_model=EventOut)
def create_event(application_id: int, data: EventCreate, db: Session = Depends(get_db)):
    app_obj = get_application(db, application_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return add_event(db, app_obj, data)
