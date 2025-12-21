from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base  # or from app.db import Base (whichever your project uses)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)