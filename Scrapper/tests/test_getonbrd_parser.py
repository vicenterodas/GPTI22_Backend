"""
Tests for the current Get on Board listing structure.
"""

from app.scrapers.base import ScrapeFilters
from app.scrapers.getonbrd import GetonbrdScraper


SAMPLE_HTML = """
<html>
<body>
    <a class="results-item" href="https://www.getonbrd.com/jobs/programming/python-engineer-acme-remote"
       title="Build APIs and data pipelines with Python.">
        <div class="results-list-info">
            <h4 class="results-list-title">
                <strong>Python Engineer</strong>
                <span class="opacity-half">Full time</span>
            </h4>
            <div class="size0">
                <strong>Acme</strong>
                <span class="location"><span>Remote</span></span>
            </div>
        </div>
        <div class="results-secondary">
            <div class="opacity-half size0">jun 01</div>
        </div>
    </a>
    <a class="results-item" href="/jobs/design/product-designer-example-santiago"
       title="Design product experiences.">
        <div class="results-list-info">
            <h4 class="results-list-title">
                <strong>Product Designer</strong>
                <span class="opacity-half">Part time</span>
            </h4>
            <div class="size0">
                <strong>Example</strong>
                <span class="location">
                    <span>Santiago This job is performed partly from home and partly at the office in: Santiago (Hybrid)</span>
                </span>
            </div>
        </div>
    </a>
</body>
</html>
"""


def test_build_search_url_uses_current_jobs_page():
    scraper = GetonbrdScraper()
    filters = ScrapeFilters(query="python", location="remote", max_pages=3)

    assert scraper.build_search_url(filters, page=3) == "https://www.getonbrd.com/jobs"


def test_parse_current_listing_cards():
    scraper = GetonbrdScraper()

    offers = scraper.parse_listings(SAMPLE_HTML)

    assert len(offers) == 2
    assert offers[0].title == "Python Engineer"
    assert offers[0].company == "Acme"
    assert offers[0].location == "Remote"
    assert offers[0].job_type == "Full time"
    assert offers[0].published_date == "jun 01"
    assert offers[0].description == "Build APIs and data pipelines with Python."
    assert offers[1].location == "Santiago"
    assert offers[1].source_url == (
        "https://www.getonbrd.com/jobs/design/product-designer-example-santiago"
    )


def test_scrape_filters_current_page_locally(monkeypatch):
    scraper = GetonbrdScraper()
    monkeypatch.setattr(scraper, "fetch_page", lambda url: SAMPLE_HTML)

    offers = scraper.scrape(ScrapeFilters(
        query="python engineer",
        location="remote",
        max_pages=5,
    ))

    assert len(offers) == 1
    assert offers[0]["title"] == "Python Engineer"
    assert offers[0]["source"] == "getonbrd"
    assert offers[0]["published_date"] is not None
