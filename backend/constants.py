import os

IDENTIFY_LOGOS_PROMPT = """
Identify the logos of all companies present in this market map.
Once identified, figure out the domain of the websites of these companies and return this result in a JSON like so: {\"company_name\": <domain_name>}",
Output in plaintext the JSON and nothing else.
Do not return a JSON list, just a single JSON dictionary with keys as company names and values as domain names.

Carefully analyze that the domain names of these companies are valid and not gibberish. Use google search if required.
"""

LOGO_DEV_API_KEY = os.environ.get("LOGO_DEV_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")

DATABASE_URL = os.environ.get("DATABASE_URL")
