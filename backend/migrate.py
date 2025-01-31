# Run this Python script to create tables
from database import Base, engine
from models import Upload

# Create the tables in the database
Base.metadata.create_all(bind=engine)
print("✅ Database tables created!")
