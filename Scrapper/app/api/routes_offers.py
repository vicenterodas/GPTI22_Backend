"""
API routes for offers and scraping.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import OfferResponse, ScrapeRequest, ScrapeResponse
from app.services.offer_service import OfferService
from app.services.scrape_service import ScrapeService
from app.scrapers.registry import list_available_scrapers

router = APIRouter()


@router.get("/", tags=["status"])
def get_status():
    """
    Health check endpoint.
    
    Returns:
        Status message and available scrapers
    """
    return {
        "status": "ok",
        "message": "Scraper API is running",
        "available_scrapers": list_available_scrapers(),
    }


@router.get("/offers", tags=["offers"], response_model=List[OfferResponse])
def list_offers(
    query: Optional[str] = None,
    source: Optional[str] = None,
    location: Optional[str] = None,
    date_range: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List job offers with optional filters.
    
    Args:
        query: Text search in title/description
        source: Filter by source (e.g., 'chiletrabajos')
        location: Filter by location
        date_range: Filter by date range ('recent', 'last_week', 'last_month')
        skip: Pagination offset
        limit: Pagination limit (max 100)
        db: Database session dependency
        
    Returns:
        List of offers matching filters
    """
    # Limit max pagination size
    limit = min(limit, 100)

    offers = OfferService.get_offers(
        db,
        query=query,
        source=source,
        location=location,
        date_range=date_range,
        skip=skip,
        limit=limit,
    )

    return offers


@router.get("/offers/{offer_id}", tags=["offers"], response_model=OfferResponse)
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    """
    Get a specific offer by ID.
    
    Args:
        offer_id: Offer ID
        db: Database session dependency
        
    Returns:
        Offer details
        
    Raises:
        HTTPException: 404 if offer not found
    """
    offer = OfferService.get_offer_by_id(db, offer_id)

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    return offer


@router.post("/scrape", tags=["scraping"], response_model=ScrapeResponse)
def scrape(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Execute a scraping operation and save new offers to database.
    
    Args:
        request: Scraping request with source, query, filters
        db: Database session dependency
        
    Returns:
        Summary of scraping results:
        - total_found: total offers found
        - new_offers_saved: new offers added to DB
        - duplicates_skipped: offers already in DB
        - errors: list of any errors that occurred
        
    Raises:
        HTTPException: 400 if request is invalid
    """
    # Validate source
    if request.source.lower() not in list_available_scrapers():
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source. Available: {list_available_scrapers()}"
        )

    # Execute scraping
    result = ScrapeService.scrape_and_save(
        db,
        source=request.source,
        query=request.query,
        location=request.location,
        date_range=request.date_range,
        max_pages=request.max_pages,
    )

    return ScrapeResponse(**result)
