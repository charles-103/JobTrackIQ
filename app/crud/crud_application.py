from sqlalchemy.orm import Session
from app.models.application import Application
from app.schemas.application import ApplicationCreate


def create_application(db: Session, data: ApplicationCreate) -> Application:
    obj = Application(
        company_name=data.company_name,
        role_title=data.role_title,
        channel=data.channel,
        location=data.location,
        jd_text=data.jd_text,
        status="active",
        current_stage="applied",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_applications(db: Session, status: str | None = None) -> list[Application]:
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()


def get_application(db: Session, application_id: int) -> Application | None:
    return db.query(Application).filter(Application.id == application_id).first()
