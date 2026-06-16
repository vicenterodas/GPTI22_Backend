"""
Tests for offer database operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models import Offer
from app.services.offer_service import OfferService


def test_delete_all_offers_preserves_table():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    try:
        session.add_all([
            Offer(
                title="Oferta Uno",
                source="computrabajo",
                source_url="https://example.com/one",
            ),
            Offer(
                title="Oferta Dos",
                source="getonbrd",
                source_url="https://example.com/two",
            ),
        ])
        session.commit()

        deleted = OfferService.delete_all_offers(session)

        assert deleted == 2
        assert OfferService.count_offers(session) == 0

        session.add(Offer(
            title="Oferta Nueva",
            source="chiletrabajos",
            source_url="https://example.com/new",
        ))
        session.commit()

        assert OfferService.count_offers(session) == 1
    finally:
        session.close()
