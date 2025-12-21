from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.company_index import CompanyIndex


def normalize_company_name(name: str) -> str:
    # 最小可用版：trim + lower + 压缩空格
    return " ".join(name.strip().lower().split())


def upsert_company_index(
    db: Session,
    *,
    name: str,
    source: str = "user_input",
) -> CompanyIndex:
    """
    如果已存在同 normalized_name：popularity+1，更新 last_seen_at
    否则新建一条
    """
    norm = normalize_company_name(name)
    if not norm:
        raise ValueError("Company name cannot be empty")

    obj = db.query(CompanyIndex).filter(CompanyIndex.normalized_name == norm).first()

    if obj:
        obj.popularity += 1
        obj.last_seen_at = datetime.utcnow()

        # 如果用户输入更“像样”的展示名，可以更新（可选）
        # 简单规则：新名字更长就覆盖
        if len(name.strip()) > len(obj.name):
            obj.name = name.strip()

        # source：保留原值 or 更新为更“权威”的来源（可选）
        # 这里简单：crawler 优先级更高
        if obj.source != "crawler" and source == "crawler":
            obj.source = "crawler"

        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    obj = CompanyIndex(
        name=name.strip(),
        normalized_name=norm,
        source=source,
        popularity=1,
        last_seen_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def suggest_companies(db: Session, *, q: str, limit: int = 10) -> List[CompanyIndex]:
    qn = normalize_company_name(q)
    if not qn:
        return []

    # 兼容 SQLite：用 lower(name) like
    # 用 normalized_name prefix 匹配最快
    rows = (
        db.query(CompanyIndex)
        .filter(CompanyIndex.normalized_name.like(f"{qn}%"))
        .order_by(desc(CompanyIndex.popularity), desc(CompanyIndex.last_seen_at))
        .limit(limit)
        .all()
    )
    return rows
