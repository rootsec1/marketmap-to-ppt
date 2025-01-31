import requests
import logging
# Local
from constants import GOOGLE_SEARCH_API_KEY

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def perform_google_search_for_company_url(company_name):
    # Base URL for the Google Custom Search JSON API
    url = "https://www.googleapis.com/customsearch/v1"

    # Parameters for the request
    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": "e50f7e709dfd04b33",
        "q": f"{company_name} vc website homepage",
        "num": 1,  # Number of search results (max 10 per request)
    }

    # Make the GET request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        search_results = response.json()
        link = str(search_results["items"][0]["link"]).strip()
        return link
    else:
        # Handle errors
        logger.error(f"Error: {response.status_code} - {response.text}")
        return None
