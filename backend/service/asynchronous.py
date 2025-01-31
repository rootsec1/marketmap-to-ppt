import asyncio
import concurrent.futures

from service.domain import get_logo_for_website
from service.object_storage import upload_file
from service.search import search_google_and_return_company_url


# Function to download all logos in parallel
async def download_logos_in_parallel(company_domains):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = await asyncio.gather(*(loop.run_in_executor(pool, get_logo_for_website, domain) for domain in company_domains))
    return results


async def get_company_website_urls_in_parallel(company_names):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = await asyncio.gather(*(loop.run_in_executor(pool, search_google_and_return_company_url, name) for name in company_names))
    return results
