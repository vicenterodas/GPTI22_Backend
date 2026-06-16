"""
Tests for the Computrabajo Chile scraper.
"""

from app.scrapers.base import ScrapeFilters
from app.scrapers.computrabajo import ComputrabajoScraper
from app.scrapers.registry import get_scraper, list_available_scrapers


SAMPLE_HTML = """
<html>
<body>
    <article class="box_offer" data-id="ABC123">
        <h2>
            <a class="js-o-link" href="/ofertas-de-trabajo/oferta-de-trabajo-de-python-developer-en-santiago-ABC123#lc=list">
                Python Developer
            </a>
        </h2>
        <p class="dFlex vm_fx fs16 fc_base mt5">
            <span class="fx_none mr10"><span class="fwB">4,2</span></span>
            <a offer-grid-article-company-url="">Empresa Uno</a>
        </p>
        <p class="fs16 fc_base mt5">
            <span class="mr10">Santiago, R.Metropolitana</span>
        </p>
        <div class="fs13 mt15">
            <span class="dIB mr10">
                <span class="icon i_salary"></span>
                $ 1.500.000,00 (Mensual)
            </span>
            <span class="dIB mr10">
                <span class="icon i_home_office"></span>
                Presencial y remoto
            </span>
        </div>
        <p class="fs13 fc_aux mt15">Hace 2 horas</p>
    </article>
    <article class="box_offer" data-id="DEF456">
        <h2>
            <a href="https://cl.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-analista-en-valparaiso-DEF456">
                Analista de Datos
            </a>
        </h2>
        <p class="dFlex vm_fx fs16 fc_base mt5">
            <a offer-grid-article-company-url="">Empresa Dos</a>
        </p>
        <p class="fs16 fc_base mt5">
            <span class="mr10">Valparaíso, Valparaíso</span>
        </p>
        <p class="fs13 fc_aux mt15">Ayer</p>
    </article>
</body>
</html>
"""


def test_build_search_url_with_filters_and_page():
    scraper = ComputrabajoScraper()
    filters = ScrapeFilters(
        query="Práctica Informática",
        location="Santiago Centro",
        date_range="last_week",
        max_pages=2,
    )

    assert scraper.build_search_url(filters, page=2) == (
        "https://cl.computrabajo.com/"
        "trabajo-de-practica-informatica-en-santiago-centro?p=2&pubdate=7"
    )


def test_parse_current_listing_cards():
    scraper = ComputrabajoScraper()

    offers = scraper.parse_listings(SAMPLE_HTML)

    assert len(offers) == 2
    assert offers[0].title == "Python Developer"
    assert offers[0].company == "Empresa Uno"
    assert offers[0].location == "Santiago, R.Metropolitana"
    assert offers[0].job_type == "Presencial y remoto"
    assert offers[0].published_date == "Hace 2 horas"
    assert offers[0].source_url == (
        "https://cl.computrabajo.com/ofertas-de-trabajo/"
        "oferta-de-trabajo-de-python-developer-en-santiago-ABC123"
    )
    assert offers[1].job_type is None


def test_scrape_paginates_and_deduplicates(monkeypatch):
    scraper = ComputrabajoScraper()
    requested_urls = []

    def mock_fetch(url):
        requested_urls.append(url)
        return SAMPLE_HTML

    monkeypatch.setattr(scraper, "fetch_page", mock_fetch)

    offers = scraper.scrape(ScrapeFilters(query="python", max_pages=3))

    assert len(offers) == 2
    assert len(requested_urls) == 2
    assert requested_urls[1].endswith("?p=2")
    assert offers[0]["source"] == "computrabajo"
    assert offers[0]["published_date"] is not None


def test_scraper_is_registered():
    assert "computrabajo" in list_available_scrapers()
    assert isinstance(get_scraper("computrabajo"), ComputrabajoScraper)
