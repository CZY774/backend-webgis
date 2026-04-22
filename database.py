from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Debug: Print all env vars
print("=== DEBUG ENV VARS ===")
print(f"DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
print(f"All env keys: {list(os.environ.keys())}")

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check Railway Variables tab.")

print(f"Using DATABASE_URL: {DATABASE_URL[:30]}...")  # Print first 30 chars only

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
