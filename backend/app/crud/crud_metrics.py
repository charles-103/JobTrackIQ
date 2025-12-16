from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.application import Application


def metrics_overview(db: Session) -> dict:
    # total
    total = db.query(func.count(Application.id)).scalar() or 0

    # group by status
    rows = (
        db.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    by_status = {status or "unknown": cnt for status, cnt in rows}

    return {"total_applications": total, "by_status": by_status}


def metrics_funnel(db: Session) -> dict:
    # total
    total = db.query(func.count(Application.id)).scalar() or 0

    # group by stage
    rows = (
        db.query(Application.current_stage, func.count(Application.id))
        .group_by(Application.current_stage)
        .all()
    )
    by_stage = {stage or "unknown": cnt for stage, cnt in rows}

    return {"total": total, "by_stage": by_stage}
