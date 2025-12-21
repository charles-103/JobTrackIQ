from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.event import Event
from app.schemas.event import EventCreate

FINAL_STATUSES = {"rejected", "offer", "closed"}

# 你可以按需扩展 interview_3 等
KNOWN_EVENT_TYPES = {"applied", "interview_1", "interview_2", "follow_up", "offer", "rejection", "closed", "reopen"}

# stage 顺序：不允许倒退
STAGE_ORDER = {
    "applied": 10,
    "interview_1": 20,
    "interview_2": 30,
    "offer": 40,
    "rejection": 90,
    "closed": 100,
}


def list_events_for_application(
    db: Session,
    application_id: int,
    limit: int = 50,
    offset: int = 0,
) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.application_id == application_id)
        .order_by(desc(Event.event_time))
        .offset(offset)
        .limit(limit)
        .all()
    )


def _is_duplicate_event(db: Session, application_id: int, event_type: str, seconds: int = 20) -> bool:
    """防连点：短时间重复同 event_type 直接拒绝"""
    last = (
        db.query(Event)
        .filter(Event.application_id == application_id, Event.event_type == event_type)
        .order_by(desc(Event.event_time))
        .first()
    )
    if not last:
        return False

    # event_time 用的是 utcnow()，这里也用 utcnow()
    return (datetime.utcnow() - last.event_time) < timedelta(seconds=seconds)


def _apply_strong_fsm(app_obj: Application, event_type: str) -> None:
    """
    强约束状态机：
    - offer/rejected/closed 为 final：只能加 reopen
    - stage 不允许倒退
    - event 驱动 status / current_stage
    """

    if event_type not in KNOWN_EVENT_TYPES:
        raise ValueError(f"Unknown event_type: {event_type}")

    # final 状态锁死：只能 reopen
    if app_obj.status in FINAL_STATUSES and event_type != "reopen":
        raise ValueError(f"Cannot add '{event_type}' when status is '{app_obj.status}'. Use 'reopen' first.")

    # reopen：回到 active + applied
    if event_type == "reopen":
        app_obj.status = "active"
        app_obj.current_stage = "applied"
        return

    # closed / offer / rejection：直接终态
    if event_type == "offer":
        app_obj.status = "offer"
        app_obj.current_stage = "offer"
        return

    if event_type == "rejection":
        app_obj.status = "rejected"
        app_obj.current_stage = "rejection"
        return

    if event_type == "closed":
        app_obj.status = "closed"
        app_obj.current_stage = "closed"
        return

    # applied：把 stage 至少设为 applied（但不强制改 status）
    if event_type == "applied":
        if not app_obj.status:
            app_obj.status = "active"
        cur = STAGE_ORDER.get(app_obj.current_stage or "applied", 0)
        if STAGE_ORDER["applied"] >= cur:
            app_obj.current_stage = "applied"
        return

    # follow_up：不改 stage，仅保证 status 有值
    if event_type == "follow_up":
        if not app_obj.status:
            app_obj.status = "active"
        return

    # interview_*：推进 stage，不允许倒退
    if event_type in {"interview_1", "interview_2"}:
        if not app_obj.status:
            app_obj.status = "active"

        current_stage = app_obj.current_stage or "applied"
        cur = STAGE_ORDER.get(current_stage, 0)
        nxt = STAGE_ORDER[event_type]

        if nxt < cur:
            raise ValueError(f"Cannot move stage backwards ({current_stage} -> {event_type}).")

        app_obj.current_stage = event_type
        return

    # 兜底：理论上到不了
    raise ValueError(f"Unhandled event_type: {event_type}")


def add_event(db: Session, application: Application, data: EventCreate) -> Event:
    # event_time：API/UI 传了就用，没传就用当前 UTC
    event_time = data.event_time or datetime.utcnow()
    event_type = data.event_type

    # 防连点/手滑
    if _is_duplicate_event(db, application.id, event_type, seconds=20):
        raise ValueError("Duplicate event too quickly. Try again later.")

    # 强约束：先更新 application 的 status / stage（可能抛 ValueError）
    _apply_strong_fsm(application, event_type)

    obj = Event(
        application_id=application.id,
        event_type=event_type,
        event_time=event_time,
        notes=data.notes,
    )

    db.add(obj)
    db.add(application)
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


def latest_events_for_applications(db: Session, application_ids: List[int]) -> Dict[int, Event]:
    if not application_ids:
        return {}

    subq = (
        db.query(
            Event.application_id.label("app_id"),
            func.max(Event.event_time).label("max_time"),
        )
        .filter(Event.application_id.in_(application_ids))
        .group_by(Event.application_id)
        .subquery()
    )

    rows = (
        db.query(Event)
        .join(
            subq,
            and_(
                Event.application_id == subq.c.app_id,
                Event.event_time == subq.c.max_time,
            ),
        )
        .all()
    )

    return {e.application_id: e for e in rows}
