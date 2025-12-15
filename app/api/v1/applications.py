from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.application import ApplicationCreate, ApplicationOut
from app.crud.crud_application import create_application, list_applications, get_application

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationOut)
def create(data: ApplicationCreate, db: Session = Depends(get_db)):
    return create_application(db, data)


@router.get("/applications", response_model=list[ApplicationOut])
def list_(status: str | None = None, db: Session = Depends(get_db)):
    return list_applications(db, status=status)


@router.get("/applications/{application_id}", response_model=ApplicationOut)
def get_(application_id: int, db: Session = Depends(get_db)):
    obj = get_application(db, application_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return obj
