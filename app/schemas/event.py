from datetime import datetime
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=60)
    event_time: datetime | None = None
    notes: str | None = None


class EventOut(BaseModel):
    id: int
    application_id: int
    event_type: str
    event_time: datetime
    notes: str | None

    model_config = {"from_attributes": True}
