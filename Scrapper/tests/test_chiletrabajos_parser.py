"""
Tests for Chiletrabajos scraper parser.
"""

import pytest
from app.scrapers.chiletrabajos import ChiletrabajosScraper
from app.scrapers.base import ScrapeFilters


# Sample HTML from Chiletrabajos (simplified structure)
SAMPLE_HTML = """
<html>
<body>
    <div class="job-item">
        <h2 class="title"><a href="/oferta/123456/practica-ingeniero-civil">Práctica Ingeniero Civil</a></h2>
        <h3 class="meta">Acme Corporation, <a>Rancagua</a></h3>
        <h3 class="meta"><a><i class="far fa-calendar"></i>hace 2 días</a></h3>
        <p class="description">Buscamos estudiante de ingeniería civil para realizar prácticas.</p>
    </div>
    <div class="job-item">
        <h2 class="title"><a href="/oferta/123457/practica-ti">Práctica Técnico Informática</a></h2>
        <h3 class="meta">Tech Solutions, <a>Valparaíso</a></h3>
        <h3 class="meta"><a><i class="far fa-calendar"></i>hace 1 semana</a></h3>
        <p class="description">Practicante en área de desarrollo de software.</p>
    </div>
    <div class="job-item">
        <h2 class="title"><a href="/oferta/123458/sin-datos">Oferta Incompleta</a></h2>
        <p class="description">Oferta con datos incompletos.</p>
    </div>
</body>
</html>
"""


@pytest.fixture
def scraper():
    """Create a ChiletrabajosScraper instance."""
    return ChiletrabajosScraper()


def test_scraper_source_name():
    """Test that scraper has correct source name."""
    scraper = ChiletrabajosScraper()
    assert scraper.source_name == "chiletrabajos"


def test_build_search_url(scraper):
    """Test URL building with filters."""
    filters = ScrapeFilters(
        query="practica industrial",
        location="1022",
        max_pages=2
    )
    
    url = scraper.build_search_url(filters, page=1)
    
    assert "https://www.chiletrabajos.cl/encuentra-un-empleo" in url
    assert "2=practica+industrial" in url or "2=practica%20industrial" in url
    assert "f=2" in url
    assert "13=1022" in url


def test_parse_listings(scraper):
    """Test parsing of job listings from HTML."""
    offers = scraper.parse_listings(SAMPLE_HTML)
    
    assert len(offers) == 3
    
    # Check first offer
    first = offers[0]
    assert first.title == "Práctica Ingeniero Civil"
    assert first.company == "Acme Corporation"
    assert first.location == "Rancagua"
    assert first.published_date == "hace 2 días"
    assert "Buscamos" in first.description
    assert "/oferta/123456/" in first.source_url
    
    # Check second offer
    second = offers[1]
    assert second.title == "Práctica Técnico Informática"
    assert second.company == "Tech Solutions"
    
    # Check third offer (incomplete)
    third = offers[2]
    assert third.title == "Oferta Incompleta"
    assert third.company is None  # Missing
    assert third.location is None  # Missing


def test_normalize_offer(scraper):
    """Test offer normalization."""
    from app.scrapers.base import RawOffer
    
    raw = RawOffer(
        title="Test Title",
        company="Test Company",
        location="Test Location",
        published_date="hace 3 días",
        description="A very long description that should be truncated " * 20,
        source_url="https://example.com/offer/123",
    )
    
    normalized = scraper.normalize_offer(raw)
    
    assert normalized["title"] == "Test Title"
    assert normalized["company"] == "Test Company"
    assert normalized["location"] == "Test Location"
    assert normalized["source"] == "chiletrabajos"
    assert normalized["source_url"] == "https://example.com/offer/123"
    assert normalized["description"] is not None
    assert len(normalized["description"]) <= 503  # 500 + "..."
    # Published date should be parsed to datetime
    assert normalized["published_date"] is not None
