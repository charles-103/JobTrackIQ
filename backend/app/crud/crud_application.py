from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_

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

def delete_application(db: Session, application_id: int) -> bool:
    obj = db.query(Application).filter(Application.id == application_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def get_application(db: Session, application_id: int) -> Application | None:
    """
    Get a single application by ID
    """
    return db.query(Application).filter(Application.id == application_id).first()


def list_applications(
    db: Session,
    *,
    status: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "created_at",
    order: str = "desc",
) -> tuple[int, list[Application]]:
    q = db.query(Application)

    if status:
        q = q.filter(Application.status == status)

    if search:
        pattern = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Application.company_name.ilike(pattern),
                Application.role_title.ilike(pattern),
            )
        )

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

def update_application_status(db: Session, application_id: int, status: str) -> Application | None:
    obj = db.query(Application).filter(Application.id == application_id).first()
    if not obj:
        return None
    obj.status = status
    db.commit()
    db.refresh(obj)
    return obj