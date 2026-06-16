"""
Command-line script to run scraping without the API.

Usage:
    python scripts/run_scraper.py --source chiletrabajos --query "practica informatica" --location "Santiago" --max-pages 2
"""

import argparse
import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add project root to sys.path so the `app` package can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal, init_db
from app.services.scrape_service import ScrapeService


def main():
    """Parse arguments and execute scraping."""
    parser = argparse.ArgumentParser(
        description="Run scraper from command line"
    )
    
    parser.add_argument(
        "--source",
        required=True,
        help="Scraper source (e.g., 'chiletrabajos')"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Search query (e.g., 'practica informatica')"
    )
    parser.add_argument(
        "--location",
        default=None,
        help="Location/region filter (optional)"
    )
    parser.add_argument(
        "--date-range",
        default=None,
        choices=["recent", "last_week", "last_month"],
        help="Date range filter (optional)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Maximum pages to scrape (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    # Get database session
    db = SessionLocal()
    
    try:
        print(f"\n🔍 Starting scrape from {args.source}...")
        print(f"   Query: {args.query}")
        if args.location:
            print(f"   Location: {args.location}")
        if args.date_range:
            print(f"   Date range: {args.date_range}")
        print(f"   Max pages: {args.max_pages}\n")
        
        # Execute scraping
        result = ScrapeService.scrape_and_save(
            db,
            source=args.source,
            query=args.query,
            location=args.location,
            date_range=args.date_range,
            max_pages=args.max_pages
        )
        
        # Print results
        print("✅ Scraping completed!")
        print(f"\n📊 Results:")
        print(f"   Total offers found: {result['total_found']}")
        print(f"   New offers saved: {result['new_offers_saved']}")
        print(f"   Duplicates skipped: {result['duplicates_skipped']}")
        
        if result['errors']:
            print(f"\n⚠️  Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"   - {error}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
