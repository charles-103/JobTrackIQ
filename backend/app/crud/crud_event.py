from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.application import Application
from app.models.event import Event
from app.schemas.event import EventCreate

def list_events_for_application(
    db: Session,
    application_id: int,
    limit: int = 50,
    offset: int = 0,
) -> list[Event]:
    return (
        db.query(Event)
        .filter(Event.application_id == application_id)
        .order_by(desc(Event.event_time))
        .offset(offset)
        .limit(limit)
        .all()
    )

def add_event(db: Session, application: Application, data: EventCreate) -> Event:
    event_time = data.event_time or datetime.utcnow()

    obj = Event(
        application_id=application.id,
        event_type=data.event_type,
        event_time=event_time,
        notes=data.notes,
    )

    # 简单规则：最新事件类型作为当前阶段
    application.current_stage = data.event_type

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_event(db: Session, event_id: int) -> bool:
    obj = db.query(Event).filter(Event.id == event_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True