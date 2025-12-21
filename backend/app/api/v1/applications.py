from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationListOut,
)
from app.crud.crud_application import (
    create_application,
    list_applications,
    get_application,
)

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationOut)
def create_application_api(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new job application
    """
    return create_application(db, data)


@router.get("/applications", response_model=ApplicationListOut)
def list_applications_api(
    status: str | None = None,
    search: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    order_by: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """
    List job applications with pagination, sorting and filtering
    """
    total, items = list_applications(
        db,
        status=status,
        search=search,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order=order,
    )

    return {
        "total": total,
        "items": items,
    }


@router.get("/applications/{application_id}", response_model=ApplicationOut)
def get_application_api(
    application_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single application by ID
    """
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application
