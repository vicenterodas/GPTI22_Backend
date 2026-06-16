"""
Scraper for Computrabajo Chile.
"""

import re
import time
import unicodedata
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.scrapers.base import BaseScraper, RawOffer, ScrapeFilters
from app.utils.dates import is_within_date_range, parse_date_string
from app.utils.text import clean_text, extract_text_snippet


class ComputrabajoScraper(BaseScraper):
    """Scraper for https://cl.computrabajo.com."""

    source_name = "computrabajo"

    LISTING_CONTAINER_SELECTOR = "article.box_offer"
    TITLE_SELECTOR = "h2 a[href*='/ofertas-de-trabajo/']"
    COMPANY_SELECTOR = "a[offer-grid-article-company-url]"
    LOCATION_SELECTOR = "p.fs16.fc_base.mt5:not(.dFlex) > span.mr10"
    DATE_SELECTOR = "p.fs13.fc_aux.mt15"

    DATE_RANGE_MAP = {
        "recent": "3",
        "last_week": "7",
        "last_month": "30",
    }

    def __init__(self):
        self.base_url = "https://cl.computrabajo.com"

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")

    def build_search_url(self, filters: ScrapeFilters, page: int = 1) -> str:
        query_slug = self._slugify(filters.query)
        path = f"/trabajo-de-{query_slug}"

        if filters.location:
            location_slug = self._slugify(filters.location)
            if location_slug:
                path += f"-en-{location_slug}"

        params = {}
        if page > 1:
            params["p"] = page

        pubdate = self.DATE_RANGE_MAP.get(filters.date_range)
        if pubdate:
            params["pubdate"] = pubdate

        query_string = urlencode(params)
        return f"{self.base_url}{path}" + (f"?{query_string}" if query_string else "")

    def fetch_page(self, url: str) -> str | None:
        headers = {
            "User-Agent": settings.DEFAULT_USER_AGENT,
            "Accept-Language": "es-CL,es;q=0.9",
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=settings.SCRAPER_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            time.sleep(settings.SCRAPER_DELAY_SECONDS)
            return response.text
        except requests.RequestException as error:
            print(f"Error fetching {url}: {error}")
            return None

    def parse_listings(self, html: str) -> list[RawOffer]:
        offers = []
        seen_urls = set()

        try:
            soup = BeautifulSoup(html, "html.parser")

            for listing in soup.select(self.LISTING_CONTAINER_SELECTOR):
                try:
                    title_elem = listing.select_one(self.TITLE_SELECTOR)
                    title = clean_text(
                        title_elem.get_text(" ", strip=True)
                    ) if title_elem else None

                    source_url = title_elem.get("href") if title_elem else None
                    if source_url and not source_url.startswith("http"):
                        source_url = self.base_url + source_url
                    if source_url:
                        source_url = source_url.split("#", 1)[0].split("?", 1)[0]

                    if not title or not source_url or source_url in seen_urls:
                        continue

                    company_elem = listing.select_one(self.COMPANY_SELECTOR)
                    company = clean_text(
                        company_elem.get_text(" ", strip=True)
                    ) if company_elem else None

                    location_elem = listing.select_one(self.LOCATION_SELECTOR)
                    location = clean_text(
                        location_elem.get_text(" ", strip=True)
                    ) if location_elem else None

                    job_type = None
                    for detail_elem in listing.select("div.fs13.mt15 span.dIB"):
                        icon_elem = detail_elem.select_one("span.icon")
                        icon_classes = icon_elem.get("class", []) if icon_elem else []
                        if "i_home_office" in icon_classes:
                            job_type = clean_text(
                                detail_elem.get_text(" ", strip=True)
                            )
                            break

                    date_elem = listing.select_one(self.DATE_SELECTOR)
                    published_date = clean_text(
                        date_elem.get_text(" ", strip=True)
                    ) if date_elem else None

                    offers.append(RawOffer(
                        title=title,
                        company=company,
                        location=location,
                        published_date=published_date,
                        job_type=job_type,
                        description=None,
                        source_url=source_url,
                    ))
                    seen_urls.add(source_url)
                except Exception as error:
                    print(f"Error parsing individual listing: {error}")

        except Exception as error:
            print(f"Error parsing listings: {error}")

        return offers

    @staticmethod
    def _parse_published_date(value: str | None) -> datetime | None:
        if not value:
            return None

        normalized = clean_text(value)
        parsed = parse_date_string(normalized)
        if parsed:
            return parsed

        lowered = normalized.lower()
        if lowered == "hoy":
            return datetime.utcnow()
        if lowered == "ayer":
            return datetime.utcnow() - timedelta(days=1)
        if "más de 30 días" in lowered or "mas de 30 dias" in lowered:
            return datetime.utcnow() - timedelta(days=31)

        return None

    def scrape(self, filters: ScrapeFilters) -> list[dict]:
        offers = []
        seen_urls = set()

        for page in range(1, filters.max_pages + 1):
            html = self.fetch_page(self.build_search_url(filters, page))
            if not html:
                break

            raw_offers = self.parse_listings(html)
            if not raw_offers:
                break

            new_urls = 0
            for raw_offer in raw_offers:
                if raw_offer.source_url in seen_urls:
                    continue

                published_date = self._parse_published_date(raw_offer.published_date)
                if not is_within_date_range(published_date, filters.date_range):
                    continue

                offers.append(self.normalize_offer(raw_offer))
                seen_urls.add(raw_offer.source_url)
                new_urls += 1

            if new_urls == 0:
                break

        return offers

    def normalize_offer(self, raw_offer: RawOffer) -> dict:
        description = raw_offer.description
        if description:
            description = extract_text_snippet(description, max_length=500)

        return {
            "title": raw_offer.title,
            "company": raw_offer.company,
            "location": raw_offer.location,
            "published_date": self._parse_published_date(raw_offer.published_date),
            "job_type": raw_offer.job_type,
            "description": description,
            "source_url": raw_offer.source_url,
            "source": self.source_name,
        }
