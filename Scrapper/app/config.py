"""
Configuration module for the scraper application.
Reads from .env file if available, otherwise uses defaults.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Settings:
    """Application settings."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./offers.db"
    )

    # Scraper Configuration
    SCRAPER_DELAY_SECONDS: float = float(os.getenv("SCRAPER_DELAY_SECONDS", "2"))
    SCRAPER_TIMEOUT_SECONDS: int = int(os.getenv("SCRAPER_TIMEOUT_SECONDS", "10"))
    DEFAULT_USER_AGENT: str = os.getenv(
        "DEFAULT_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Testing
    RUN_INTEGRATION_TESTS: bool = os.getenv(
        "RUN_INTEGRATION_TESTS", 
        "false"
    ).lower() in ("true", "1", "yes")


settings = Settings()
