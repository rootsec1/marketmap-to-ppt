import uuid
import os
import logging

from minio import Minio

# Local
from models import Upload


logger = logging.getLogger()
logger.setLevel(logging.INFO)


client = Minio(
    "localhost:9000",
    access_key="fJNdZEcpIQjmZChhX5uL",
    secret_key="FBiUqZFqxyQZjitLCRgjvICppfNkEkfFK4j0voT4",
    secure=False,
)

bucket_name = "assets"
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)


def upload_file(filepath: str, folder: str, db):
    # Last element of the path is the filename
    filename = filepath.split("/")[-1]
    # Use hash of file at filepath to avoid conflicts
    input_object_name = f"{folder}/{uuid.uuid4().hex}_{filename}"
    client.fput_object(bucket_name, input_object_name, filepath)
    logger.info(f"✅ Uploaded input file to MinIO: {input_object_name}")
    # Delete file from local storage
    os.remove(filepath)

    new_upload_record = Upload(
        filename=filename,
        s3_key=input_object_name,
        domain_name=filename.replace(".jpg", "") if folder == "logos" else None,
        upload_type=folder,
    )

    db.add(new_upload_record)
    db.commit()
    db.refresh(new_upload_record)
    return input_object_name


def get_pre_signed_url_for_object(object_name: str):
    return client.presigned_get_object(bucket_name, object_name)
