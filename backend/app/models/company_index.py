from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CompanyIndex(Base):
    __tablename__ = "company_index"

    __table_args__ = (
        UniqueConstraint("normalized_name", name="uq_company_index_normalized_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 展示给用户看的名字（可保留大小写）
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # 归一化后的名字（用于搜索 & 去重）
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # 来源：user_input / crawler / seed
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="user_input")

    # 用过多少次（热度）
    popularity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    last_seen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
