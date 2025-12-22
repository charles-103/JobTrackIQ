from __future__ import annotations

import httpx


async def fetch_greenhouse_jobs(board_token: str) -> list[dict]:
    """
    Greenhouse public job board endpoint (no login):
    https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    # data: {"jobs":[...]}
    return data.get("jobs", [])

async def fetch_greenhouse_jobs(board_token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    return data.get("jobs", [])


async def fetch_greenhouse_job_detail(board_token: str, job_id: int) -> dict:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
