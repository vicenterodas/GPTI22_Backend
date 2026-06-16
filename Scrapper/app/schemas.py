"""
Pydantic schemas for API requests and responses.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OfferBase(BaseModel):
    """Base schema for offer data."""

    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    published_date: Optional[datetime] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    source: str
    source_url: str


class OfferCreate(OfferBase):
    """Schema for creating a new offer."""

    pass


class OfferResponse(OfferBase):
    """Schema for API response with offer data."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScrapeRequest(BaseModel):
    """Schema for scraping request."""

    source: str = Field(..., description="Scraper source name, e.g. 'chiletrabajos'")
    query: str = Field(..., description="Search query, e.g. 'practica informatica'")
    location: Optional[str] = Field(None, description="Location/region filter")
    date_range: Optional[str] = Field(
        None,
        description="Date range filter: 'recent', 'last_week', 'last_month'"
    )
    max_pages: int = Field(1, ge=1, le=20, description="Maximum pages to scrape")


class ScrapeResponse(BaseModel):
    """Schema for scraping response."""

    source: str
    query: str
    total_found: int
    new_offers_saved: int
    duplicates_skipped: int
    errors: list[str] = []
