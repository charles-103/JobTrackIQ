from __future__ import annotations

import httpx
from typing import Optional
from app.ingest.greenhouse import fetch_greenhouse_jobs, fetch_greenhouse_job_detail
from app.ingest.lever import fetch_lever_jobs
from app.ingest.smartrecruiters import fetch_smartrecruiters_jobs


async def smart_import(company_name: str, fetch_jd: bool = False) -> dict:
    """
    智能导入：根据公司名称自动尝试所有平台
    
    Args:
        company_name: 公司名称
        fetch_jd: 是否获取完整JD
        
    Returns:
        {
            "source": "greenhouse" | "lever" | "smartrecruiters" | None,
            "jobs": [...],
            "company_name": "...",
            "identifier": "..." (用于后续获取JD)
        }
    """
    company_name_lower = company_name.lower().strip()
    
    # 尝试 Greenhouse（使用公司名作为 board_token）
    try:
        jobs = await fetch_greenhouse_jobs(company_name_lower)
        if jobs and len(jobs) > 0:
            return {
                "source": "greenhouse",
                "jobs": jobs,
                "company_name": company_name,
                "identifier": company_name_lower,
            }
    except Exception:
        pass
    
    # 尝试 Lever（使用公司名作为 site）
    try:
        jobs = await fetch_lever_jobs(company_name_lower)
        if jobs and len(jobs) > 0:
            return {
                "source": "lever",
                "jobs": jobs,
                "company_name": company_name,
                "identifier": company_name_lower,
            }
    except Exception:
        pass
    
    # 尝试 SmartRecruiters（使用公司名作为 identifier）
    try:
        jobs = await fetch_smartrecruiters_jobs(company_name_lower)
        if jobs and len(jobs) > 0:
            return {
                "source": "smartrecruiters",
                "jobs": jobs,
                "company_name": company_name,
                "identifier": company_name_lower,
            }
    except Exception:
        pass
    
    # 如果都失败了，返回空结果
    return {
        "source": None,
        "jobs": [],
        "company_name": company_name,
        "identifier": None,
    }


async def get_job_details(source: str, identifier: str, job_id: int, fetch_jd: bool = False) -> Optional[str]:
    """根据来源获取职位详情"""
    if not fetch_jd:
        return None
        
    try:
        if source == "greenhouse":
            detail = await fetch_greenhouse_job_detail(identifier, job_id)
            return detail.get("content")
        # Lever 和 SmartRecruiters 的详情已经在列表中包含了
        return None
    except Exception:
        return None






