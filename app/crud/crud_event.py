from datetime import datetime
from sqlalchemy.orm import Session
from app.models.application import Application
from app.models.event import Event
from app.schemas.event import EventCreate


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
