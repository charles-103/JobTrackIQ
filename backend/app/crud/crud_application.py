from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.models.application import Application
from app.schemas.application import ApplicationCreate


def create_application(db: Session, data: ApplicationCreate) -> Application:
    """
    Create a new job application
    """
    payload = data.model_dump()

    # Ensure defaults (in case schema doesn't include these fields)
    payload.setdefault("status", "active")
    payload.setdefault("current_stage", "applied")

    obj = Application(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_application(db: Session, application_id: int) -> Application | None:
    """
    Get a single application by ID
    """
    return db.query(Application).filter(Application.id == application_id).first()


def list_applications(
    db: Session,
    *,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "created_at",
    order: str = "desc",
) -> tuple[int, list[Application]]:
    """
    List applications with pagination, filtering and sorting
    """
    q = db.query(Application)

    if status:
        q = q.filter(Application.status == status)

    total = q.count()

    allowed_order_fields = {
        "created_at": Application.created_at,
        "updated_at": Application.updated_at,
        "company_name": Application.company_name,
        "role_title": Application.role_title,
    }

    order_column = allowed_order_fields.get(order_by, Application.created_at)

    if order.lower() == "asc":
        q = q.order_by(asc(order_column))
    else:
        q = q.order_by(desc(order_column))

    items = q.offset(offset).limit(limit).all()
    return total, items