from datetime import datetime
from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    role_title: str = Field(min_length=1, max_length=200)
    channel: str | None = None
    location: str | None = None
    jd_text: str | None = None


class ApplicationOut(BaseModel):
    id: int
    company_name: str
    role_title: str
    channel: str | None
    location: str | None
    status: str
    current_stage: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
