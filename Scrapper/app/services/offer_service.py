"""
Service for managing job offers in the database.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import Offer as OfferModel
from app.schemas import OfferCreate, OfferResponse
from app.utils.dates import is_within_date_range


class OfferService:
    """Service for database operations on offers."""

    @staticmethod
    def create_offer(db: Session, offer_data: dict) -> OfferModel | None:
        """
        Create a new offer in the database.
        
        Args:
            db: Database session
            offer_data: Dictionary with offer fields
            
        Returns:
            Created OfferModel or None if duplicate (unique constraint)
        """
        try:
            offer = OfferModel(**offer_data)
            db.add(offer)
            db.commit()
            db.refresh(offer)
            return offer
        except Exception as e:
            db.rollback()
            print(f"Error creating offer: {e}")
            return None

    @staticmethod
    def get_offers(
        db: Session,
        query: Optional[str] = None,
        source: Optional[str] = None,
        location: Optional[str] = None,
        date_range: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[OfferModel]:
        """
        Get offers from database with optional filters.
        
        Args:
            db: Database session
            query: Text search in title or description
            source: Filter by source (e.g., 'chiletrabajos')
            location: Filter by location
            date_range: Filter by date range ('recent', 'last_week', 'last_month')
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of matching offers
        """
        db_query = db.query(OfferModel)

        # Text search filter
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    OfferModel.title.ilike(search_term),
                    OfferModel.description.ilike(search_term)
                )
            )

        # Source filter
        if source:
            db_query = db_query.filter(OfferModel.source == source)

        # Location filter
        if location:
            search_location = f"%{location}%"
            db_query = db_query.filter(OfferModel.location.ilike(search_location))

        # Get results before date filtering (done in-memory)
        offers = db_query.order_by(OfferModel.published_date.desc()).all()

        # Filter by date range (in-memory)
        if date_range:
            offers = [
                o for o in offers
                if is_within_date_range(o.published_date, date_range)
            ]

        # Apply pagination
        return offers[skip : skip + limit]

    @staticmethod
    def get_offer_by_id(db: Session, offer_id: int) -> OfferModel | None:
        """
        Get a single offer by ID.
        
        Args:
            db: Database session
            offer_id: ID of offer
            
        Returns:
            OfferModel or None if not found
        """
        return db.query(OfferModel).filter(OfferModel.id == offer_id).first()

    @staticmethod
    def get_offer_by_source_url(db: Session, source: str, source_url: str) -> OfferModel | None:
        """
        Check if an offer already exists by source and URL.
        
        Args:
            db: Database session
            source: Source name (e.g., 'chiletrabajos')
            source_url: URL from source
            
        Returns:
            OfferModel if exists, None otherwise
        """
        return db.query(OfferModel).filter(
            and_(
                OfferModel.source == source,
                OfferModel.source_url == source_url
            )
        ).first()

    @staticmethod
    def get_recent_offers(db: Session, source: Optional[str] = None, limit: int = 50) -> list[OfferModel]:
        """
        Get the most recently saved offers for a source or all sources.
        
        Args:
            db: Database session
            source: Scraper source name, or None for all sources
            limit: Maximum number of offers to return
        
        Returns:
            List of recent offers
        """
        query = db.query(OfferModel)
        
        if source is not None:
            query = query.filter(OfferModel.source == source)
        
        return (
            query
            .order_by(OfferModel.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_offers(db: Session) -> int:
        """
        Get total number of offers in database.
        
        Args:
            db: Database session
            
        Returns:
            Total count
        """
        return db.query(OfferModel).count()

    @staticmethod
    def delete_all_offers(db: Session) -> int:
        """
        Delete all offers while preserving the database and table structure.

        Returns:
            Number of deleted offers.
        """
        try:
            deleted = db.query(OfferModel).delete(synchronize_session=False)
            db.commit()
            return deleted
        except Exception:
            db.rollback()
            raise
