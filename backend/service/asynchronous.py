import asyncio
import concurrent.futures

from service.domain import get_favicon_for_website
from service.search import perform_google_search_for_company_url


# Function to download all logos in parallel
async def download_logos_in_parallel(company_domains):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = await asyncio.gather(*(loop.run_in_executor(pool, get_favicon_for_website, domain) for domain in company_domains))
    return results


async def get_company_website_urls_in_parallel(company_names):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = await asyncio.gather(*(loop.run_in_executor(pool, perform_google_search_for_company_url, name) for name in company_names))
    return results
