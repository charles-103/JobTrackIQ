from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class JobPostingCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    role_title: str = Field(min_length=1, max_length=255)
    location: str | None = None
    url: str | None = None
    jd_text: str | None = None


class JobPostingOut(BaseModel):
    id: int
    source: str
    company_name: str
    role_title: str
    location: str | None
    url: str | None
    posted_at: datetime | None
    jd_text: str | None
    fingerprint: str
    created_at: datetime

    class Config:
        from_attributes = True
