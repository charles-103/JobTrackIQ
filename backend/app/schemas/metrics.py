from pydantic import BaseModel


class MetricsOverviewOut(BaseModel):
    total_applications: int
    by_status: dict[str, int]


class MetricsFunnelOut(BaseModel):
    total: int
    by_stage: dict[str, int]
