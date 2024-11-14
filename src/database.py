from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base


# Create database URL

DATABASE_URL = "postgresql://postgres:password@localhost:5432/school"
# create engine
engine = create_engine(DATABASE_URL)

# create SessionLocal

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# declarative base

Base = declarative_base()
