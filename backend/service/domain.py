import requests
import re
import os

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
        logger.info(f"Domain starts http: {website_url}")
        domain = re.sub(r"https?://(www\.)?", "", website_url).split("/")[0]
    # Check cache for existing logo
    if os.path.exists(f"tmp/{domain}.jpg"):
        logger.info(f"Logo for {domain} already exists, skipping...")
        return f"tmp/{domain}.jpg"

    url = f"https://img.logo.dev/{domain}?token={LOGO_DEV_API_KEY}&retina=true&size=300"
    # Download image from URL and save it to the local directory tmp/ with the domain name as the filename
    logger.info(f"Fetching logo for {domain}...")
    response = requests.get(url)
    if not response.ok:
        raise Exception(f"Failed to fetch logo for {website_url}")

    with open(f"tmp/{domain}.jpg", "wb") as f:
        f.write(response.content)
    return f"tmp/{domain}.jpg"
