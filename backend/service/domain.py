import requests
import re
import os
import favicon
import logging

# Local
from constants import LOGO_DEV_API_KEY
from service.object_storage import upload_file


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_logo_for_website(website_url: str) -> str:
    # use regex to remove http://, https://, www. from the website_url and get the main domain name
    # e.g. https://www.google.com -> google.com
    domain = website_url
    if website_url.startswith("http"):
        domain = re.sub(r"https?://(www\.)?", "", website_url).split("/")[0]
        logger.info(f"Domain before: {website_url}, after: {domain}")
    # Check cache for existing logo
    if os.path.exists(f"tmp/{domain}.jpg"):
        logger.info(f"Logo for {domain} already exists, skipping...")
        return f"tmp/{domain}.jpg"

    url = f"https://img.logo.dev/{domain}?token={LOGO_DEV_API_KEY}&retina=true&size=300"
    # Download image from URL and save it to the local directory tmp/ with the domain name as the filename
    logger.info(f"Fetching logo for {domain}...")
    response = requests.get(url)
    if not response.ok:
        return None

    with open(f"tmp/{domain}.jpg", "wb") as f:
        f.write(response.content)
    return f"tmp/{domain}.jpg"


def get_favicon_for_website(website_url: str) -> str:
    try:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        domain = re.sub(r"https?://(www\.)?", "", website_url).split("/")[0]
        # Check cache for existing logo
        if os.path.exists(f"tmp/{domain}.jpg"):
            logger.info(f"Logo for {domain} already exists, skipping...")
            return f"tmp/{domain}.jpg"

        logger.info(f"Fetching favicon for {domain}...")
        icons = favicon.get(website_url, headers={'User-Agent': user_agent})
        icon = icons[0]
        logger.info(f"Icon URL: {icon.url}")

        response = requests.get(icon.url, stream=True, headers={'User-Agent': user_agent})
        if not response.ok:
            return None
        with open(f"/tmp/{domain}.jpg", "wb") as image:
            for chunk in response.iter_content(1024):
                image.write(chunk)
        return f"/tmp/{domain}.jpg"
    except:
        return get_logo_for_website(website_url)
