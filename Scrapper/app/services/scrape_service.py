"""
Service for orchestrating scraping operations.
"""

from sqlalchemy.orm import Session
from app.scrapers.base import ScrapeFilters
from app.scrapers.registry import get_scraper
from app.services.offer_service import OfferService


class ScrapeService:
    """Service for managing scraping operations."""

    @staticmethod
    def scrape_and_save(
        db: Session,
        source: str,
        query: str,
        location: str | None = None,
        date_range: str | None = None,
        max_pages: int = 1
    ) -> dict:
        """
        Scrape job offers and save new ones to database.
        
        Args:
            db: Database session
            source: Source name (e.g., 'chiletrabajos')
            query: Search query
            location: Optional location filter
            date_range: Optional date range filter
            max_pages: Max pages to scrape
            
        Returns:
            Dictionary with results:
            {
                'source': str,
                'total_found': int,
                'new_offers_saved': int,
                'duplicates_skipped': int,
                'errors': list[str]
            }
        """
        errors = []

        # Get scraper
        scraper = get_scraper(source)
        if not scraper:
            return {
                "source": source,
                "total_found": 0,
                "new_offers_saved": 0,
                "duplicates_skipped": 0,
                "errors": [f"Unknown source: {source}"],
            }

        # Build filters
        filters = ScrapeFilters(
            query=query,
            location=location,
            date_range=date_range,
            max_pages=max_pages
        )

        # Scrape
        try:
            offers = scraper.scrape(filters)
        except Exception as e:
            errors.append(f"Scraping failed: {str(e)}")
            return {
                "source": source,
                "total_found": 0,
                "new_offers_saved": 0,
                "duplicates_skipped": 0,
                "errors": errors,
            }

        # Save to database
        new_offers = 0
        duplicates = 0

        for offer_data in offers:
            # Check if already exists
            existing = OfferService.get_offer_by_source_url(
                db,
                offer_data["source"],
                offer_data["source_url"]
            )

            if existing:
                duplicates += 1
                continue

            # Save new offer
            result = OfferService.create_offer(db, offer_data)
            if result:
                new_offers += 1
            else:
                errors.append(f"Failed to save: {offer_data['title']}")

        return {
            "source": source,
            "total_found": len(offers),
            "new_offers_saved": new_offers,
            "duplicates_skipped": duplicates,
            "errors": errors,
        }
