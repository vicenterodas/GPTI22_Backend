# Project Structure

```
Scrapper/
│
├── README.md                          # Project documentation
├── ../requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── ../.gitignore                         # Git ignore rules
│
├── app/                               # Main application package
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration (from .env or defaults)
│   ├── models.py                      # SQLAlchemy database models
│   ├── schemas.py                     # Pydantic API schemas
│   ├── database.py                    # Database setup and session management
│   │
│   ├── api/                           # REST API routes
│   │   ├── __init__.py
│   │   └── routes_offers.py           # Endpoints: /offers, /scrape, etc.
│   │
│   ├── scrapers/                      # Job portal scrapers
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract BaseScraper class
│   │   ├── chiletrabajos.py           # Chiletrabajos.cl scraper implementation
│   │   └── registry.py                # Scraper registry (extensible)
│   │
│   ├── services/                      # Business logic services
│   │   ├── __init__.py
│   │   ├── offer_service.py           # Database operations on offers
│   │   └── scrape_service.py          # Scraping orchestration
│   │
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── text.py                    # Text processing (clean, snippet)
│       └── dates.py                   # Date parsing and filtering
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures and configuration
│   ├── test_chiletrabajos_parser.py   # Unit tests for parser
│   ├── test_offer_normalization.py    # Unit tests for utilities
│   └── test_api_offers.py             # Integration tests for API
│
└── scripts/                           # Utility scripts
    └── run_scraper.py                 # CLI scraper (no API needed)
```

## Data Flow Diagram

### 1. Scraping via API

```
Client Request
    ↓
POST /scrape { source, query, location, date_range, max_pages }
    ↓
FastAPI Route Handler (routes_offers.py)
    ↓
ScrapeService.scrape_and_save()
    ↓
Registry.get_scraper("chiletrabajos")
    ↓
ChiletrabajosScraper.scrape(filters)
    ├─→ build_search_url(filters, page=1)
    ├─→ fetch_page(url) → HTML
    ├─→ parse_listings(html) → [RawOffer]
    ├─→ normalize_offer(raw_offer) → dict
    ├─→ [repeat for pages 2, 3, ...]
    └─→ Returns [normalized offers]
    ↓
For each offer:
    ├─→ Check if duplicate via OfferService.get_offer_by_source_url()
    └─→ If new: OfferService.create_offer() → SQLite INSERT
    ↓
Response: { total_found, new_saved, duplicates_skipped, errors }
```

### 2. Querying Offers

```
Client Request
    ↓
GET /offers?query=practica&source=chiletrabajos&location=Santiago
    ↓
FastAPI Route Handler
    ↓
OfferService.get_offers(query, source, location, date_range)
    ↓
SQLAlchemy Query
    ├─→ Filter by text search (title, description)
    ├─→ Filter by source
    ├─→ Filter by location
    ├─→ Apply date range filtering
    └─→ Pagination (skip, limit)
    ↓
Returns [OfferResponse] → JSON
```

### 3. CLI Scraping

```
python scripts/run_scraper.py --source chiletrabajos --query "practica"
    ↓
Parse command-line arguments
    ↓
Initialize database
    ↓
Call ScrapeService.scrape_and_save() [same as API flow]
    ↓
Display results (found, saved, duplicates, errors)
```

## Component Responsibilities

### BaseScraper (base.py)
- **Purpose**: Abstract interface for all scrapers
- **Ensures**: All scrapers implement the same contract
- **Methods**:
  - `build_search_url()` - Construct search URLs with filters
  - `fetch_page()` - HTTP request with headers, timeout, delays
  - `parse_listings()` - Extract listings from HTML
  - `normalize_offer()` - Convert to standard Offer format
  - `scrape()` - Orchestrates fetch → parse → normalize for multiple pages

### ChiletrabajosScraper (chiletrabajos.py)
- **Purpose**: Implement Chiletrabajos-specific scraping
- **Key Details**:
  - Uses `requests + BeautifulSoup` (no JavaScript)
  - CSS selectors isolated in class attributes (easy to update)
  - Gracefully handles missing data
  - Includes User-Agent, timeout, and configurable delays
  - Parses "hace X días" date format

### Registry (registry.py)
- **Purpose**: Central registry of all scrapers
- **Key Feature**: Add new scrapers by just registering the class
- **Enables**: API to load scrapers by name without direct imports

### OfferService (offer_service.py)
- **Purpose**: All database operations
- **Methods**:
  - `create_offer()` - Save new offer (handles duplicates via constraints)
  - `get_offers()` - Query with filters
  - `get_offer_by_source_url()` - Check for duplicates

### ScrapeService (scrape_service.py)
- **Purpose**: Orchestrate scraping and persistence
- **Flow**:
  1. Get scraper from registry
  2. Run scraper
  3. For each offer: check if duplicate, save if new
  4. Return summary (found, saved, duplicates, errors)

### Utilities
- **text.py**: `clean_text()`, `extract_text_snippet()`
- **dates.py**: `parse_relative_date()`, `is_within_date_range()`

## Extensibility Examples

### Adding a New Scraper

**Step 1**: Create `app/scrapers/getonboard.py`

```python
from app.scrapers.base import BaseScraper, RawOffer, ScrapeFilters

class GetOnBoardScraper(BaseScraper):
    source_name = "getonboard"
    
    def build_search_url(self, filters: ScrapeFilters, page: int = 1) -> str:
        # Implement for GetOnBoard
        pass
    
    def fetch_page(self, url: str) -> str | None:
        # Use requests + headers
        pass
    
    def parse_listings(self, html: str) -> list[RawOffer]:
        # Parse with BeautifulSoup
        pass
    
    def normalize_offer(self, raw_offer: RawOffer) -> dict:
        # Convert to standard format
        pass
```

**Step 2**: Register in `app/scrapers/registry.py`

```python
from app.scrapers.getonboard import GetOnBoardScraper

SCRAPERS = {
    "chiletrabajos": ChiletrabajosScraper,
    "getonboard": GetOnBoardScraper,  # Add here
}
```

**Step 3**: Add tests in `tests/test_getonboard_parser.py`

**Step 4**: Use via API or CLI

```bash
# API
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"source": "getonboard", "query": "python developer", "max_pages": 1}'

# CLI
python scripts/run_scraper.py --source getonboard --query "python developer"
```

### Changing Chiletrabajos Selectors

If the site structure changes, only update selectors in `ChiletrabajosScraper`:

```python
class ChiletrabajosScraper(BaseScraper):
    # Just update these lines if site changes
    LISTING_CONTAINER_SELECTOR = "div.new-class"
    TITLE_SELECTOR = "h3.title"  # Was "h2 a"
    # ... rest unchanged
```

## Test Architecture

### Unit Tests (No Network)
- **test_chiletrabajos_parser.py**: Parser tests with sample HTML
- **test_offer_normalization.py**: Utilities tests (text, dates)
- **test_api_offers.py**: API logic tests (with mocked scraper)

Run with: `pytest`

### Integration Tests (Real Network)
- Marked with `@pytest.mark.integration`
- Disabled by default (no network hammering)
- Enable with: `RUN_INTEGRATION_TESTS=1 pytest -m integration`

## Error Handling Strategy

1. **Scraper**: If `fetch_page()` fails, stop pagination (returns what was collected)
2. **Parser**: If a listing fails to parse, skip it (continue with others)
3. **Database**: If save fails (e.g., duplicate), continue with next offer
4. **API**: Returns `ScrapeResponse` with `errors` list (never crashes)

## Performance Considerations

1. **Delays**: Configurable `SCRAPER_DELAY_SECONDS` (default 2) between requests
2. **Timeouts**: Configurable `SCRAPER_TIMEOUT_SECONDS` (default 10)
3. **Pagination**: Limited to `max_pages` parameter
4. **Database**: SQLite OK for MVP; PostgreSQL recommended for production
5. **No Proxies**: Direct requests only (for transparency)

## Security Notes

- No credentials stored
- No authentication on API (for academic/local use)
- User-Agent included to identify as scraper
- Respects server delays
- No rate limiting bypass attempts
