from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.metrics import MetricsOverviewOut, MetricsFunnelOut
from app.crud.crud_metrics import metrics_overview, metrics_funnel

router = APIRouter(tags=["metrics"])


@router.get("/metrics/overview", response_model=MetricsOverviewOut)
def overview(db: Session = Depends(get_db)):
    return metrics_overview(db)


@router.get("/metrics/funnel", response_model=MetricsFunnelOut)
def funnel(db: Session = Depends(get_db)):
    return metrics_funnel(db)
