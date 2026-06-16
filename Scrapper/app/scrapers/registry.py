"""
Registry of available scrapers.

This module maintains a mapping of scraper names to scraper classes.
When adding a new scraper:
1. Create the scraper class in its own module
2. Import it here
3. Add it to the SCRAPERS dictionary

This allows the API to fetch scrapers by name without importing them directly
in the route handlers, making the system more maintainable and testable.
"""

from typing import Type, Dict
from app.scrapers.base import BaseScraper
from app.scrapers.chiletrabajos import ChiletrabajosScraper
from app.scrapers.computrabajo import ComputrabajoScraper
from app.scrapers.getonbrd import GetonbrdScraper

# Registry of all available scrapers
# Key: source name (lowercase)
# Value: scraper class
SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "chiletrabajos": ChiletrabajosScraper,
    "computrabajo": ComputrabajoScraper,
    "getonbrd": GetonbrdScraper,
    # Future scrapers can be added here:
    # "trabajando": TrabajandoScraper,
    # "laborum": LaborumScraper,
}


def get_scraper(source_name: str) -> BaseScraper | None:
    """
    Get a scraper instance by name.
    
    Args:
        source_name: Name of scraper (lowercase)
        
    Returns:
        Scraper instance or None if not found
    """
    source_name = source_name.lower()

    if source_name not in SCRAPERS:
        return None

    scraper_class = SCRAPERS[source_name]
    return scraper_class()


def list_available_scrapers() -> list[str]:
    """
    Get list of available scraper names.
    
    Returns:
        List of scraper source names
    """
    return list(SCRAPERS.keys())
