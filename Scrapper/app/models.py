"""
SQLAlchemy models for the database.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Offer(Base):
    """
    Database model for job offers.
    
    Stores normalized job postings from various sources.
    Uses (source, source_url) as unique constraint to prevent duplicates.
    """

    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True, index=True)
    published_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    job_type = Column(String(100), nullable=True)
    source = Column(String(100), nullable=False, index=True)
    source_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Prevent duplicate offers from the same source
    __table_args__ = (
        UniqueConstraint("source", "source_url", name="uq_source_url"),
    )
