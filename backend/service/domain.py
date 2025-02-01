import backoff
import requests
import re
import os
import favicon
import logging
import time
from PIL import Image
from google.api_core.exceptions import ResourceExhausted

# Local
from constants import LOGO_DEV_API_KEY
from service.gemini import prompt_gemini


logger = logging.getLogger()
logger.setLevel(logging.INFO)

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'


def get_favicon_for_website(website_url: str) -> str:
    try:
        domain = re.sub(r"https?://(www\.)?", "", website_url).split("/")[0]
        # Check cache for existing logo
        if os.path.exists(f"tmp/{domain}.jpg"):
            logger.info(f"Logo for {domain} already exists, skipping...")
            return f"tmp/{domain}.jpg"

        logger.info(f"Fetching favicon for {domain}...")
        icons = favicon.get(website_url, headers={'User-Agent': UA})
        icon = icons[0]
        logger.info(f"Icon URL: {icon.url}, extension: {icon.format}")

        response = requests.get(icon.url, stream=True, headers={'User-Agent': UA})
        if not response.ok:
            return None

        filename = f"tmp/{domain}.{icon.format}"
        logger.info(f"Saving favicon to {filename}...")
        with open(f"/tmp/{domain}.{icon.format}", "wb") as image:
            for chunk in response.iter_content(1024):
                image.write(chunk)

        if filename.endswith(".ico"):
            logger.info(f"Converting favicon to PNG for {icon.url}...")
            img = Image.open(f"/tmp/{domain}.jpg")
            img.save(f"/tmp/{domain}.png", "png")
            return f"/tmp/{domain}.png"

        return f"/tmp/{domain}.jpg"
    except:
        return None


def custom_backoff(details):
    wait_time = 2 ** details['tries']
    logger.info(f"Retrying {details['target']} in {wait_time} seconds...")
    # Wait 3 seconds before prompting Gemini to scrape HTML
    time.sleep(3)


@backoff.on_exception(backoff.expo, ResourceExhausted, max_tries=3, on_backoff=custom_backoff)
def scrape_and_download_logo(website):
    try:
        domain_name = re.sub(r"https?://(www\.)?", "", website).split("/")[0]

        if os.path.exists(f"tmp/{domain_name}.jpg"):
            logger.info(f"✅ Logo for {domain_name} already exists, skipping...")
            return f"tmp/{domain_name}.jpg"

        logger.info(f"🔎 Processing {website}...")

        # Step 1: Fetch website HTML
        response = requests.get(website, headers={"User-Agent": UA}, timeout=10)
        response.raise_for_status()  # Raise error if the request fails
        html_content = response.text

        # Step 2: Extract logo URL using Gemini
        prompt = f"""
        You are an expert web scraper. Given the HTML content of a company's website, extract the primary logo image URL.
        Return a JSON object like this: {{"logo_url": <EXTRACTED_LOGO_URL>}}.
        If the URL is incomplete like so: /themes/custom/baincapital/images/logo.svg, prepend the domain name to it, ensure HTTPS, and return the full URL.
        If the URL contains something like "cloud.google.com", "pypi.org", or "npmjs.com", it is not the primary logo. Please find the primary logo.
        If you can't find it, return {{"logo_url": null}}. Do not output anything else.
        
        HTML:
        {html_content}
        """

        llm_response = prompt_gemini(prompt)
        logger.info(f"LLM Response: {llm_response}")
        logo_url: str = llm_response.get("logo_url")

        # Step 3: Validate logo URL
        if not logo_url or logo_url == "null":
            logger.info(f"❌ No logo found for {domain_name}. Falling back to favicon.")
            return get_favicon_for_website(website)

        if not (logo_url.endswith(".jpg") or logo_url.endswith(".png")):
            logger.info(f"❌ Invalid logo format for {domain_name}. Falling back to favicon.")
            return get_favicon_for_website(website)

        if domain_name not in logo_url:
            logger.info(f"❌ Logo URL does not match domain. Falling back to favicon.")
            return get_favicon_for_website(website)

        # Step 4: Download and save the logo
        os.makedirs("tmp", exist_ok=True)
        file_path = f"tmp/{domain_name}.jpg"

        img_response = requests.get(logo_url, stream=True)
        img_response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)
        logger.info(f"✅ Logo saved: {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        logger.info(f"❌ Error processing {website}: {e}")
        return get_favicon_for_website(website)


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

    url = f"https://img.logo.dev/{domain}?token={LOGO_DEV_API_KEY}&retina=true&size=300&fallback=404&format=jpg"
    # Download image from URL and save it to the local directory tmp/ with the domain name as the filename
    logger.info(f"Fetching logo for {domain}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        if not response.ok:
            return None

        with open(f"tmp/{domain}.jpg", "wb") as f:
            f.write(response.content)
        return f"tmp/{domain}.jpg"
    except:
        return scrape_and_download_logo(website_url)
