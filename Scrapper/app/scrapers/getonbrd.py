"""
Scraper for Getonbrd.com job portal.

This scraper handles:
- Building search URLs with filters
- Fetching HTML pages with proper User-Agent and timeout
- Parsing job listings from HTML using BeautifulSoup
- Normalizing offers to common format

Note: Getonbrd may load content dynamically; this scraper attempts static HTML parsing.
"""

import json
import time
import unicodedata
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.scrapers.base import BaseScraper, RawOffer, ScrapeFilters
from app.utils.text import clean_text, extract_text_snippet
from app.utils.dates import is_within_date_range, parse_date_string


class GetonbrdScraper(BaseScraper):
    """Scraper for https://www.getonbrd.com"""

    source_name = "getonbrd"

    # CSS selectors - these may need adjustment if site structure changes
    LISTING_CONTAINER_SELECTOR = "a.results-item[href*='/jobs/']"
    TITLE_SELECTOR = ".results-list-title strong"
    JOB_TYPE_SELECTOR = ".results-list-title > span.opacity-half"
    COMPANY_SELECTOR = ".results-list-info .size0 > strong"
    LOCATION_SELECTOR = ".results-list-info .location"
    DATE_SELECTOR = ".results-secondary .opacity-half.size0"

    def __init__(self):
        """Initialize scraper with base URL."""
        self.base_url = "https://www.getonbrd.com"
        self.search_path = "/jobs"

    def build_search_url(self, filters: ScrapeFilters, page: int = 1) -> str:
        """
        Build Getonbrd search URL.
        
        Get on Board currently exposes all listings on the jobs page and ignores
        the old q/location/page query parameters. Filtering is therefore applied
        locally in scrape().
        
        Args:
            filters: Search filters including query, location, date_range
            page: Page number (1-indexed)
            
        Returns:
            Full URL string
        """
        return f"{self.base_url}{self.search_path}"

    def fetch_page(self, url: str) -> str | None:
        """
        Fetch HTML from a Getonbrd URL with proper headers and timeout.
        
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
        Parse HTML and extract job listings from Getonbrd.
        
        Getonbrd uses JSON-LD structured data for jobs.
        Falls back to DOM parsing if JSON data not available.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of RawOffer objects
        """
        offers = []

        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Try to extract JSON-LD job postings first
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    data = json.loads(script.string or "")
                    entries = data if isinstance(data, list) else [data]
                    if isinstance(data, dict) and isinstance(data.get("@graph"), list):
                        entries.extend(data["@graph"])

                    for entry in entries:
                        if not isinstance(entry, dict) or entry.get("@type") != "JobPosting":
                            continue

                        title = entry.get("title")
                        url = entry.get("url")
                        company_data = entry.get("hiringOrganization", {})
                        company = company_data.get("name") if isinstance(company_data, dict) else None
                        job_location = entry.get("jobLocation", {})
                        location = None
                        if isinstance(job_location, dict):
                            address = job_location.get("address", {})
                            if isinstance(address, dict):
                                location = address.get("addressLocality") or address.get("addressCountry")
                        
                        published_date_str = entry.get("datePosted")
                        description = entry.get("description")
                        job_type = entry.get("employmentType")
                        
                        if title and url:
                            offer = RawOffer(
                                title=title,
                                company=company,
                                location=location,
                                published_date=published_date_str,
                                job_type=job_type,
                                description=description,
                                source_url=url,
                            )
                            offers.append(offer)
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

            # If JSON-LD parsing didn't yield results, try DOM parsing
            if not offers:
                seen_urls = set()
                for listing in soup.select(self.LISTING_CONTAINER_SELECTOR):
                    try:
                        title_elem = listing.select_one(self.TITLE_SELECTOR)
                        title = clean_text(title_elem.get_text(" ", strip=True)) if title_elem else None

                        source_url = listing.get("href")
                        if source_url and not source_url.startswith("http"):
                            source_url = self.base_url + source_url
                        if source_url:
                            source_url = source_url.split("?", 1)[0]

                        if not title or not source_url or source_url in seen_urls:
                            continue

                        company_elem = listing.select_one(self.COMPANY_SELECTOR)
                        company = clean_text(company_elem.get_text(" ", strip=True)) if company_elem else None

                        location_container = listing.select_one(self.LOCATION_SELECTOR)
                        location_elem = (
                            location_container.select_one(".tooltipster")
                            if location_container
                            else None
                        ) or location_container
                        location = clean_text(location_elem.get_text(" ", strip=True)) if location_elem else None
                        location = self._clean_location(location)

                        date_elem = listing.select_one(self.DATE_SELECTOR)
                        published_date = clean_text(date_elem.get_text(" ", strip=True)) if date_elem else None

                        job_type_elem = listing.select_one(self.JOB_TYPE_SELECTOR)
                        job_type = clean_text(job_type_elem.get_text(" ", strip=True)) if job_type_elem else None

                        description = clean_text(listing.get("title"))

                        offers.append(RawOffer(
                            title=title,
                            company=company,
                            location=location,
                            published_date=published_date,
                            job_type=job_type,
                            description=description,
                            source_url=source_url,
                        ))
                        seen_urls.add(source_url)
                    except Exception as e:
                        print(f"Error parsing individual listing: {e}")
                        continue

        except Exception as e:
            print(f"Error parsing listings: {e}")

        return offers

    @staticmethod
    def _normalize_filter_text(value: str | None) -> str:
        if not value:
            return ""

        normalized = unicodedata.normalize("NFKD", value)
        return " ".join(
            normalized.encode("ascii", "ignore").decode("ascii").lower().split()
        )

    @staticmethod
    def _clean_location(value: str | None) -> str | None:
        if not value:
            return None

        for separator in (" This job is ", " Position is "):
            value = value.split(separator, 1)[0]

        return clean_text(value)

    def _matches_filters(self, offer: RawOffer, filters: ScrapeFilters) -> bool:
        searchable_text = self._normalize_filter_text(" ".join(filter(None, [
            offer.title,
            offer.company,
            offer.location,
            offer.job_type,
            offer.description,
        ])))
        query_terms = self._normalize_filter_text(filters.query).split()

        if query_terms and not all(term in searchable_text for term in query_terms):
            return False

        location = self._normalize_filter_text(filters.location)
        offer_location = self._normalize_filter_text(offer.location)
        if location and location not in offer_location:
            return False

        published_date = self._parse_published_date(offer.published_date)
        return is_within_date_range(published_date, filters.date_range)

    @staticmethod
    def _parse_published_date(value: str | None) -> datetime | None:
        parsed = parse_date_string(value)
        if parsed or not value:
            return parsed

        try:
            parsed = datetime.strptime(value.strip(), "%b %d").replace(
                year=datetime.utcnow().year
            )
            if parsed > datetime.utcnow():
                parsed = parsed.replace(year=parsed.year - 1)
            return parsed
        except ValueError:
            return None

    def scrape(self, filters: ScrapeFilters) -> list[dict]:
        url = self.build_search_url(filters)
        html = self.fetch_page(url)
        if not html:
            return []

        return [
            self.normalize_offer(offer)
            for offer in self.parse_listings(html)
            if self._matches_filters(offer, filters)
        ]

    def normalize_offer(self, raw_offer: RawOffer) -> dict:
        """
        Convert RawOffer to normalized format for database.
        
        Args:
            raw_offer: Raw offer from parser
            
        Returns:
            Dictionary ready for database insertion
        """
        # Try to parse published_date if available
        published_date = self._parse_published_date(raw_offer.published_date)

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
