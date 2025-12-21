from app.api.v1.applications import router as applications_router
from app.api.v1.events import router as events_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.companies import router as companies_router

all_routers = [
    applications_router,
    events_router,
    metrics_router,
    companies_router,
]
