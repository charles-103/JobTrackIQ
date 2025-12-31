from __future__ import annotations

import httpx
from bs4 import BeautifulSoup


async def fetch_workday_jobs(careers_site_url: str, company_name: str = None) -> list[dict]:
    """
    Workday careers page scraper
    
    Note: Workday doesn't have a public API, so we scrape the careers page.
    This is more fragile and may break if Workday changes their HTML structure.
    
    Args:
        careers_site_url: Full URL to the Workday careers page
                        (e.g., "https://example.wd3.myworkdayjobs.com/careers")
        company_name: Company name (if not provided, will try to extract from page)
    """
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.get(careers_site_url)
        r.raise_for_status()
        html = r.text
    
    # Parse HTML to extract job listings
    # Note: This is a simplified parser - Workday pages can vary
    soup = BeautifulSoup(html, 'html.parser')
    jobs = []
    
    # Common Workday selectors (may need adjustment per company)
    job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and 'job' in x.lower() if x else False)
    
    for element in job_elements[:50]:  # Limit to first 50 to avoid too many
        title_elem = element.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower() if x else False)
        location_elem = element.find(['span', 'div'], class_=lambda x: x and 'location' in x.lower() if x else False)
        link_elem = element.find('a', href=True)
        
        if title_elem:
            title = title_elem.get_text(strip=True)
            location = location_elem.get_text(strip=True) if location_elem else None
            url = link_elem['href'] if link_elem else None
            
            if title:
                jobs.append({
                    'title': title,
                    'location': location,
                    'url': url if url and url.startswith('http') else None,
                })
    
    return jobs






