"""
Scraper for Chiletrabajos.cl job portal.

This scraper handles:
- Building search URLs with filters
- Fetching HTML pages with proper User-Agent and timeout
- Parsing job listings from HTML using BeautifulSoup
- Normalizing offers to common format

Key design decisions:
- Uses requests + BeautifulSoup (no JavaScript needed for initial version)
- Includes delays between requests to be respectful
- Handles missing data gracefully (returns None instead of breaking)
- CSS selectors are isolated in class attributes for easy updating
"""

import time
import requests
from bs4 import BeautifulSoup
from typing import Optional
from datetime import datetime
from urllib.parse import urlencode

from app.config import settings
from app.scrapers.base import BaseScraper, RawOffer, ScrapeFilters
from app.utils.text import clean_text, extract_text_snippet
from app.utils.dates import parse_relative_date
class ChiletrabajosScraper(BaseScraper):
    """Scraper for https://www.chiletrabajos.cl"""

    source_name = "chiletrabajos"

    # CSS selectors - these are the key points to update if site structure changes
    LISTING_CONTAINER_SELECTOR = "div.job-item"
    TITLE_SELECTOR = "h2.title a"
    DESCRIPTION_SELECTOR = "p.description"
    URL_SELECTOR = "h2.title a"
    LOCATION_MAP = {
        "santiago": "1022",
        "valparaíso": "1014",
        "valparaiso": "1014",
        "concepción": "1035",
        "concepcion": "1035",
    }

    def __init__(self):
        """Initialize scraper with base URL."""
        self.base_url = "https://www.chiletrabajos.cl"
        self.search_path = "/encuentra-un-empleo"

    def get_job_type_from_detail(self, url: str) -> str | None:
        """
        Fetch the detail page and extract the job type from the info table.

        Args:
            url: Detail page URL

        Returns:
            The job type string or None if not found
        """
        html = self.fetch_page(url)
        if not html:
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select("table.table tbody tr")
            for row in rows:
                cells = row.select("td")
                if len(cells) == 2:
                    label = clean_text(cells[0].get_text(strip=True)).lower()
                    if "tipo" in label:
                        return clean_text(cells[1].get_text(strip=True))
        except Exception:
            return None

        return None

    def build_search_url(self, filters: ScrapeFilters, page: int = 1) -> str:
        """
        Build Chiletrabajos search URL.
        
        URL format: https://www.chiletrabajos.cl/encuentra-un-empleo?
                    2=query&f=2&13=region&page=page
        
        Args:
            filters: Search filters including query, location, date_range
            page: Page number (1-indexed)
            
        Returns:
            Full URL string
        """
        params = {
            "2": filters.query,
            "f": "2",
        }

        if filters.location:
            normalized_location = filters.location.strip().lower()
            if normalized_location in self.LOCATION_MAP:
                params["13"] = self.LOCATION_MAP[normalized_location]
            elif filters.location.isdigit():
                params["13"] = filters.location
            else:
                # If location is textual but unknown, include it in the search query.
                params["2"] = f"{filters.query} {filters.location}".strip()

        if page > 1:
            params["page"] = page

        query_string = urlencode(params)
        url = f"{self.base_url}{self.search_path}?{query_string}"

        return url

    def fetch_page(self, url: str) -> str | None:
        """
        Fetch HTML from a Chiletrabajos URL with proper headers and timeout.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        headers = {
            "User-Agent": settings.DEFAULT_USER_AGENT,
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=settings.SCRAPER_TIMEOUT_SECONDS
            )
            response.raise_for_status()

            # Add delay between requests to be respectful
            time.sleep(settings.SCRAPER_DELAY_SECONDS)

            return response.text

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_listings(self, html: str) -> list[RawOffer]:
        """
        Parse HTML and extract job listings from Chiletrabajos.
        
        Handles missing elements gracefully - missing data returns None
        instead of raising exceptions.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of RawOffer objects
        """
        offers = []

        try:
            soup = BeautifulSoup(html, "html.parser")
            listings = soup.select(self.LISTING_CONTAINER_SELECTOR)

            if not listings:
                return offers

            for listing in listings:
                try:
                    # Extract each field safely
                    title_elem = listing.select_one(self.TITLE_SELECTOR)
                    title = clean_text(title_elem.get_text(strip=True)) if title_elem else None

                    # Some Chiletrabajos cards include company and location together.
                    company = None
                    location = None
                    company_meta = listing.select("h3.meta")
                    if company_meta:
                        company_location_text = clean_text(company_meta[0].get_text(" ", strip=True))
                        location_elem = company_meta[0].select_one("a")
                        location = clean_text(location_elem.get_text(strip=True)) if location_elem else None
                        if location and company_location_text.endswith(location):
                            company = clean_text(company_location_text[:-len(location)].rstrip(", "))
                        else:
                            company = company_location_text

                    published_date_str = None
                    if len(company_meta) > 1:
                        published_date_str = clean_text(company_meta[1].get_text(strip=True))

                    description_elem = listing.select_one(self.DESCRIPTION_SELECTOR)
                    description = clean_text(description_elem.get_text(strip=True)) if description_elem else None

                    url_elem = listing.select_one(self.URL_SELECTOR)
                    source_url = None
                    if url_elem and url_elem.get("href"):
                        source_url = url_elem.get("href")
                        # Make absolute URL if relative
                        if not source_url.startswith("http"):
                            source_url = self.base_url + source_url

                    # Only add if we have at least a title and URL
                    if title and source_url:
                        offer = RawOffer(
                            title=title,
                            company=company,
                            location=location,
                            published_date=published_date_str,
                            job_type=None,
                            description=description,
                            source_url=source_url,
                        )
                        offers.append(offer)

                except Exception as e:
                    print(f"Error parsing individual listing: {e}")
                    continue

        except Exception as e:
            print(f"Error parsing listings: {e}")

        return offers

    def normalize_offer(self, raw_offer: RawOffer) -> dict:
        """
        Convert RawOffer to normalized format for database.
        
        Args:
            raw_offer: Raw offer from parser
            
        Returns:
            Dictionary ready for database insertion
        """
        # Try to parse published_date if available
        published_date = None
        if raw_offer.published_date:
            # Try relative or absolute date parsing
            from app.utils.dates import parse_date_string
            published_date = parse_date_string(raw_offer.published_date)

        # Limit description snippet
        description = raw_offer.description
        if description:
            description = extract_text_snippet(description, max_length=500)

        return {
            "title": raw_offer.title,
            "company": raw_offer.company,
            "location": raw_offer.location,
            "published_date": published_date,
            "job_type": raw_offer.job_type,
            "description": description,
            "source_url": raw_offer.source_url,
            "source": self.source_name,
        }
