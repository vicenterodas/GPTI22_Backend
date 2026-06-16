"""
Tests for FastAPI API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_status(client):
    """Test GET / endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "available_scrapers" in data
    assert "chiletrabajos" in data["available_scrapers"]


def test_list_offers_empty(client):
    """Test GET /offers with empty database."""
    response = client.get("/offers")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_list_offers_with_filters(client, db_session):
    """Test GET /offers with various filters."""
    from app.models import Offer as OfferModel
    from datetime import datetime
    
    # Add some test offers
    offer1 = OfferModel(
        title="Práctica Ingeniería",
        company="Company A",
        location="Santiago",
        description="Ingeniería civil",
        source="chiletrabajos",
        source_url="https://example.com/1",
        published_date=datetime.utcnow(),
    )
    offer2 = OfferModel(
        title="Práctica TI",
        company="Company B",
        location="Valparaíso",
        description="Desarrollo de software",
        source="chiletrabajos",
        source_url="https://example.com/2",
        published_date=datetime.utcnow(),
    )
    
    db_session.add(offer1)
    db_session.add(offer2)
    db_session.commit()
    
    # Test listing all offers
    response = client.get("/offers")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test text search
    response = client.get("/offers?query=Ingeniería")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Práctica Ingeniería"
    
    # Test location filter
    response = client.get("/offers?location=Valparaíso")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["location"] == "Valparaíso"
    
    # Test source filter
    response = client.get("/offers?source=chiletrabajos")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_offer_by_id(client, db_session):
    """Test GET /offers/{offer_id} endpoint."""
    from app.models import Offer as OfferModel
    from datetime import datetime
    
    offer = OfferModel(
        title="Test Offer",
        company="Test Company",
        location="Test Location",
        source="chiletrabajos",
        source_url="https://example.com/test",
        published_date=datetime.utcnow(),
    )
    
    db_session.add(offer)
    db_session.commit()
    
    # Get offer
    response = client.get(f"/offers/{offer.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Offer"
    assert data["company"] == "Test Company"
    
    # Get non-existent offer
    response = client.get("/offers/9999")
    assert response.status_code == 404


def test_scrape_invalid_source(client):
    """Test POST /scrape with invalid source."""
    response = client.post(
        "/scrape",
        json={
            "source": "nonexistent",
            "query": "test",
            "max_pages": 1
        }
    )
    assert response.status_code == 400
    assert "Unknown source" in response.json()["detail"]


def test_scrape_chiletrabajos_mock(client, db_session, monkeypatch):
    """Test POST /scrape with mocked scraper."""
    # Mock the scraper to avoid real network calls
    def mock_scrape(self, filters):
        return [
            {
                "title": "Mock Offer 1",
                "company": "Mock Company",
                "location": "Mock Location",
                "published_date": None,
                "description": "Mock description",
                "source_url": "https://example.com/mock1",
                "source": "chiletrabajos",
            }
        ]
    
    from app.scrapers.chiletrabajos import ChiletrabajosScraper
    monkeypatch.setattr(ChiletrabajosScraper, "scrape", mock_scrape)
    
    # Call scrape endpoint
    response = client.post(
        "/scrape",
        json={
            "source": "chiletrabajos",
            "query": "practica",
            "max_pages": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "chiletrabajos"
    assert data["total_found"] == 1
    assert data["new_offers_saved"] == 1
    assert data["duplicates_skipped"] == 0
    
    # Verify offer was saved
    response = client.get("/offers")
    assert len(response.json()) == 1


def test_scrape_duplicate_handling(client, db_session, monkeypatch):
    """Test that duplicate offers are not saved."""
    from app.models import Offer as OfferModel
    from datetime import datetime
    
    # Pre-populate with an offer
    existing_offer = OfferModel(
        title="Existing Offer",
        company="Company",
        location="Location",
        source="chiletrabajos",
        source_url="https://example.com/existing",
        published_date=datetime.utcnow(),
    )
    db_session.add(existing_offer)
    db_session.commit()
    
    # Mock scraper to return the same offer
    def mock_scrape(self, filters):
        return [
            {
                "title": "Existing Offer",
                "company": "Company",
                "location": "Location",
                "published_date": None,
                "description": "Description",
                "source_url": "https://example.com/existing",  # Same URL
                "source": "chiletrabajos",
            }
        ]
    
    from app.scrapers.chiletrabajos import ChiletrabajosScraper
    monkeypatch.setattr(ChiletrabajosScraper, "scrape", mock_scrape)
    
    # Call scrape endpoint
    response = client.post(
        "/scrape",
        json={
            "source": "chiletrabajos",
            "query": "practica",
            "max_pages": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] == 1
    assert data["new_offers_saved"] == 0
    assert data["duplicates_skipped"] == 1
    
    # Verify no new offers were added
    response = client.get("/offers")
    assert len(response.json()) == 1  # Still just the original
