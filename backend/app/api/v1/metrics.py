from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.metrics import MetricsOverviewOut, MetricsFunnelOut
from app.crud.crud_metrics import metrics_overview, metrics_time_to_milestones, metrics_by_channel


router = APIRouter(tags=["metrics"])


@router.get("/metrics/overview")
def overview(db: Session = Depends(get_db)):
    base = metrics_overview(db)
    timing = metrics_time_to_milestones(db)
    channels = metrics_by_channel(db, min_samples=1)

    return {
        **base,
        **timing,
        "channels": channels,
    }