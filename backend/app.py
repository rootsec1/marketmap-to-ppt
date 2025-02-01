from dotenv import load_dotenv
load_dotenv()

import shutil
import time
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Depends
from sqlalchemy.orm import Session


# Local imports
from database import SessionLocal
from service.object_storage import *
from service.presentation import *
from service.asynchronous import *
from service.gemini import *
from constants import *

# Create a tmp directory to store files before uploading to object storage
os.makedirs("tmp", exist_ok=True)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_market_map(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Received file: {file.filename}")
    file_location = f"tmp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"File saved to {file_location}")

    company_domain_dict: dict = prompt_gemini(IDENTIFY_LOGOS_PROMPT, file_location)
    company_names = list(company_domain_dict.keys())
    # company_domains = company_domain_dict.values()

    company_website_urls = await get_company_website_urls_in_parallel(company_names)
    # Filter out None values
    company_website_urls = [url for url in company_website_urls if url]

    logger.info(f"Company website URLs: {company_website_urls}")

    # Upload file to object storage
    uploaded_file_object_name = upload_file(file_location, "inputs", db)
    uploaded_file_presigned_url = get_pre_signed_url_for_object(uploaded_file_object_name)
    logger.info(f"Uploaded file to object storage: {uploaded_file_object_name}")

    # Fetch logos for identified companies
    logger.info("Fetching logos for identified companies in parallel")
    downloaded_logos = await download_logos_in_parallel(company_website_urls)
    downloaded_logos = [logo for logo in downloaded_logos if logo]

    logger.info(f"Downloaded logos: {downloaded_logos}")
    presentation_file_path = create_ppt_with_logos(downloaded_logos)
    logger.info(f"Created presentation file: {presentation_file_path}")

    # Upload presentation file to object storage
    presentation_object_name = upload_file(presentation_file_path, "outputs", db)
    presentation_presigned_url = get_pre_signed_url_for_object(presentation_object_name)
    logger.info(f"Uploaded presentation file to object storage: {presentation_object_name}")

    # Remove downloaded logos from filesystem
    for logo in downloaded_logos:
        if os.path.exists(logo):
            upload_file(logo, "logos", db)
    logger.info("Removed downloaded logos from filesystem")

    # Return presentation file as response to the user so they can download it
    return {
        "companies": company_domain_dict,
        "presentation_link": presentation_presigned_url,
        "uploaded_image_link": uploaded_file_presigned_url
    }


@app.get("/analyze_text")
async def analyze_market_map_text(query: str, db: Session = Depends(get_db)):
    logger.info(f"Received query: {query}")
    company_domain_dict: dict = prompt_gemini(FIX_COMPANY_NAMES_PROMPT.format(query=query))
    company_names = list(company_domain_dict.keys())

    company_website_urls = await get_company_website_urls_in_parallel(company_names)
    # Fetch logos for identified companies
    logger.info("Fetching logos for identified companies in parallel")
    downloaded_logos = await download_logos_in_parallel(company_website_urls)
    downloaded_logos = [logo for logo in downloaded_logos if logo]

    logger.info(f"Downloaded logos: {downloaded_logos}")
    presentation_file_path = create_ppt_with_logos(downloaded_logos)
    logger.info(f"Created presentation file: {presentation_file_path}")

    # Upload presentation file to object storage
    presentation_object_name = upload_file(presentation_file_path, "outputs", db)
    presentation_presigned_url = get_pre_signed_url_for_object(presentation_object_name)
    logger.info(f"Uploaded presentation file to object storage: {presentation_object_name}")

    # Remove downloaded logos from filesystem
    for logo in downloaded_logos:
        if os.path.exists(logo):
            upload_file(logo, "logos", db)
    logger.info("Removed downloaded logos from filesystem")

    # Return presentation file as response to the user so they can download it
    return {
        "companies": company_domain_dict,
        "presentation_link": presentation_presigned_url,
        "query": query
    }
