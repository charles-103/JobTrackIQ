from __future__ import annotations

import httpx


async def fetch_lever_jobs(site: str) -> list[dict]:
    """
    Lever public job board endpoint (no login):
    https://api.lever.co/v0/postings/{site}
    
    Args:
        site: Lever site identifier (e.g., "lever" for lever.co/lever)
    """
    url = f"https://api.lever.co/v0/postings/{site}"
    
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    
    # Lever returns list directly: [{"id": "...", "text": "...", ...}, ...]
    return data if isinstance(data, list) else []


async def fetch_lever_job_detail(site: str, job_id: str) -> dict:
    """
    Fetch detailed job posting from Lever
    
    Args:
        site: Lever site identifier
        job_id: Job posting ID
    """
    url = f"https://api.lever.co/v0/postings/{site}/{job_id}"
    
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()






