"""
Base scraper class and interfaces.
All specific scrapers should inherit from BaseScraper.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class RawOffer:
    """
    Raw offer data from scraper before normalization.
    """

    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    published_date: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None


@dataclass
class ScrapeFilters:
    """Filters for scraping requests."""

    query: str
    location: Optional[str] = None
    date_range: Optional[str] = None
    max_pages: int = 1


class BaseScraper(ABC):
    """
    Abstract base class for all job offer scrapers.
    
    Defines the contract that all scrapers must implement.
    Allows for flexibility in implementation while maintaining consistency.
    """

    source_name: str  # e.g., "chiletrabajos", "getonboard"

    @abstractmethod
    def build_search_url(self, filters: ScrapeFilters, page: int = 1) -> str:
        """
        Build a search URL for the given filters and page number.
        
        Args:
            filters: Search filters
            page: Page number (1-indexed)
            
        Returns:
            URL string to fetch
        """
        pass

    @abstractmethod
    def fetch_page(self, url: str) -> str | None:
        """
        Fetch HTML content from a URL.
        
        Includes error handling, User-Agent, and timeout.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        pass

    @abstractmethod
    def parse_listings(self, html: str) -> list[RawOffer]:
        """
        Parse HTML and extract job listings.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of RawOffer objects extracted from HTML
        """
        pass

    @abstractmethod
    def normalize_offer(self, raw_offer: RawOffer) -> dict:
        """
        Convert a RawOffer to normalized offer format for database storage.
        
        Args:
            raw_offer: Raw offer from parser
            
        Returns:
            Dictionary with keys: title, company, location, published_date,
            description, source_url, source
        """
        pass

    def scrape(self, filters: ScrapeFilters) -> list[dict]:
        """
        Main scraping method. Orchestrates fetch -> parse -> normalize.
        
        Args:
            filters: Search filters
            
        Returns:
            List of normalized offer dictionaries
        """
        all_offers = []

        for page in range(1, filters.max_pages + 1):
            url = self.build_search_url(filters, page=page)
            html = self.fetch_page(url)

            if not html:
                break  # Stop if fetch fails

            raw_offers = self.parse_listings(html)
            if not raw_offers:
                break  # Stop if no offers found

            for raw_offer in raw_offers:
                normalized = self.normalize_offer(raw_offer)
                all_offers.append(normalized)

        return all_offers
