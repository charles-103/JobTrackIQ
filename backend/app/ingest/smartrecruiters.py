from __future__ import annotations

import httpx


async def fetch_smartrecruiters_jobs(company_identifier: str) -> list[dict]:
    """
    SmartRecruiters public job board endpoint:
    https://api.smartrecruiters.com/public-api/v1/companies/{company_identifier}/postings
    
    Args:
        company_identifier: Company identifier in SmartRecruiters
    """
    url = f"https://api.smartrecruiters.com/public-api/v1/companies/{company_identifier}/postings"
    
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    
    # SmartRecruiters returns: {"content": [...], "totalFound": ...}
    return data.get("content", [])


async def fetch_smartrecruiters_job_detail(company_identifier: str, job_id: str) -> dict:
    """
    Fetch detailed job posting from SmartRecruiters
    
    Args:
        company_identifier: Company identifier
        job_id: Job posting ID
    """
    url = f"https://api.smartrecruiters.com/public-api/v1/companies/{company_identifier}/postings/{job_id}"
    
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()






