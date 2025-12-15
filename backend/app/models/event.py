from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), index=True)

    event_type: Mapped[str] = mapped_column(String(60), index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    application = relationship("Application", back_populates="events")
