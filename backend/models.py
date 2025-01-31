from sqlalchemy import Column, Integer, String
from database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    domain_name = Column(String, nullable=True, default=None)
    upload_type = Column(String, nullable=False)
