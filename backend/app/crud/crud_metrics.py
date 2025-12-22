from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.application import Application
from app.models.event import Event


def metrics_overview(db: Session) -> dict:
    total = db.query(func.count(Application.id)).scalar() or 0

    # by_status
    rows = (
        db.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    by_status = { (s or "unknown"): c for s, c in rows }

    offer = by_status.get("offer", 0)
    rejected = by_status.get("rejected", 0)

    offer_rate = (offer / total) if total else 0.0
    rejection_rate = (rejected / total) if total else 0.0

    return {
        "total_applications": total,
        "by_status": by_status,
        "offer_rate": offer_rate,
        "rejection_rate": rejection_rate,
    }


def metrics_time_to_milestones(db: Session) -> dict:
    """
    平均耗时（天）：
    - created_at -> first interview (interview_1 or interview_2)
    - created_at -> offer
    兼容 SQLite / Postgres
    """

    # first_interview_time per application
    interview_subq = (
        db.query(
            Event.application_id.label("app_id"),
            func.min(Event.event_time).label("first_interview_time"),
        )
        .filter(Event.event_type.in_(["interview_1", "interview_2"]))
        .group_by(Event.application_id)
        .subquery()
    )

    # offer_time per application
    offer_subq = (
        db.query(
            Event.application_id.label("app_id"),
            func.min(Event.event_time).label("offer_time"),
        )
        .filter(Event.event_type == "offer")
        .group_by(Event.application_id)
        .subquery()
    )

    dialect = db.bind.dialect.name  # "postgresql" / "sqlite" / ...

    if dialect == "postgresql":
        # epoch seconds / 86400 -> days
        avg_days_to_interview = (
            db.query(
                func.avg(
                    func.extract("epoch", interview_subq.c.first_interview_time - Application.created_at) / 86400.0
                )
            )
            .join(interview_subq, interview_subq.c.app_id == Application.id)
            .scalar()
        )

        avg_days_to_offer = (
            db.query(
                func.avg(
                    func.extract("epoch", offer_subq.c.offer_time - Application.created_at) / 86400.0
                )
            )
            .join(offer_subq, offer_subq.c.app_id == Application.id)
            .scalar()
        )

    else:
        # SQLite fallback (julianday exists)
        avg_days_to_interview = (
            db.query(
                func.avg(func.julianday(interview_subq.c.first_interview_time) - func.julianday(Application.created_at))
            )
            .join(interview_subq, interview_subq.c.app_id == Application.id)
            .scalar()
        )

        avg_days_to_offer = (
            db.query(
                func.avg(func.julianday(offer_subq.c.offer_time) - func.julianday(Application.created_at))
            )
            .join(offer_subq, offer_subq.c.app_id == Application.id)
            .scalar()
        )

    return {
        "avg_days_to_interview": float(avg_days_to_interview) if avg_days_to_interview is not None else None,
        "avg_days_to_offer": float(avg_days_to_offer) if avg_days_to_offer is not None else None,
    }


def metrics_by_channel(db: Session, min_samples: int = 1) -> list[dict]:
    """
    每个 channel：
    - total
    - offers
    - offer_rate
    """
    # offers = sum(case when status='offer' then 1 else 0 end)
    offer_case = func.sum(case((Application.status == "offer", 1), else_=0))

    rows = (
        db.query(
            Application.channel,
            func.count(Application.id).label("total"),
            offer_case.label("offers"),
        )
        .group_by(Application.channel)
        .having(func.count(Application.id) >= min_samples)
        .order_by(func.count(Application.id).desc())
        .all()
    )

    out = []
    for channel, total, offers in rows:
        rate = (offers / total) if total else 0.0
        out.append(
            {
                "channel": channel or "unknown",
                "total": int(total),
                "offers": int(offers),
                "offer_rate": float(rate),
            }
        )
    return out
