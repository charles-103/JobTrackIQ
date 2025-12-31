from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, UniqueConstraint, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

from app.core.database import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_job_postings_fingerprint"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    jd_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_jd: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_skills: Mapped[list[str] | None] = mapped_column(PG_ARRAY(String), nullable=True)

    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
