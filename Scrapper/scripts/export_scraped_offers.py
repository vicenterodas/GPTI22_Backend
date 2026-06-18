"""
Run the scraper app in an isolated process and export scraped offers as JSON.

This script is intentionally used from the Flask app through subprocess because
both applications use the top-level package name "app".
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from datetime import date, datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal, init_db  # noqa: E402
from app.scrapers.registry import list_available_scrapers  # noqa: E402
from app.services.offer_service import OfferService  # noqa: E402
from app.services.scrape_service import ScrapeService  # noqa: E402


def json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def offer_to_dict(offer):
    return {
        "title": offer.title,
        "company": offer.company,
        "location": offer.location,
        "published_date": offer.published_date,
        "job_type": offer.job_type,
        "description": offer.description,
        "source": offer.source,
        "source_url": offer.source_url,
        "created_at": offer.created_at,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="practica")
    parser.add_argument("--location", default=None)
    parser.add_argument("--date-range", default=None)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--sources", default="")
    return parser.parse_args()


def main():
    args = parse_args()
    init_db()

    available_sources = list_available_scrapers()
    selected_sources = [
        source.strip().lower()
        for source in args.sources.split(",")
        if source.strip()
    ] or available_sources

    selected_sources = [
        source for source in selected_sources if source in available_sources
    ]

    db = SessionLocal()
    results = []
    errors = []

    try:
        for source in selected_sources:
            with contextlib.redirect_stdout(sys.stderr):
                result = ScrapeService.scrape_and_save(
                    db,
                    source=source,
                    query=args.query,
                    location=args.location,
                    date_range=args.date_range,
                    max_pages=args.max_pages,
                )

            results.append(result)
            errors.extend(result.get("errors", []))

        offers = OfferService.get_recent_offers(db, limit=500)
        payload = {
            "results": results,
            "errors": errors,
            "offers": [offer_to_dict(offer) for offer in offers],
        }
        print(json.dumps(payload, default=json_default, ensure_ascii=False))
    finally:
        db.close()


if __name__ == "__main__":
    main()
