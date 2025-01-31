import asyncio
import concurrent.futures

from service.domain import get_logo_for_website
from service.object_storage import upload_file


# Function to download all logos in parallel
async def download_logos_in_parallel(company_domains):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = await asyncio.gather(*(loop.run_in_executor(pool, get_logo_for_website, domain) for domain in company_domains))
    return results
