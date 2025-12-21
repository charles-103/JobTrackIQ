from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.crud_company import suggest_companies

router = APIRouter(tags=["companies"])


@router.get("/companies/suggest")
def companies_suggest(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    rows = suggest_companies(db, q=q, limit=limit)
    return [{"id": r.id, "name": r.name, "source": r.source} for r in rows]
