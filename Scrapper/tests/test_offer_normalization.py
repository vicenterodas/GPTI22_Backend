"""
Tests for offer normalization utilities.
"""

import pytest
from app.utils.text import clean_text, extract_text_snippet
from app.utils.dates import parse_relative_date, is_within_date_range
from datetime import datetime, timedelta


class TestTextCleaning:
    """Tests for text.py utilities."""

    def test_clean_text_simple(self):
        """Test cleaning simple text."""
        result = clean_text("  hello   world  ")
        assert result == "hello world"

    def test_clean_text_multiple_spaces(self):
        """Test cleaning text with multiple spaces."""
        result = clean_text("hello    \t\t   world")
        assert result == "hello world"

    def test_clean_text_newlines(self):
        """Test cleaning text with newlines."""
        result = clean_text("hello\n\n\nworld")
        assert result == "hello world"

    def test_clean_text_none(self):
        """Test cleaning None returns None."""
        result = clean_text(None)
        assert result is None

    def test_clean_text_empty(self):
        """Test cleaning empty string returns None."""
        result = clean_text("   ")
        assert result is None

    def test_extract_snippet_short_text(self):
        """Test snippet extraction on short text."""
        text = "This is a short text"
        result = extract_text_snippet(text, max_length=50)
        assert result == text

    def test_extract_snippet_long_text(self):
        """Test snippet extraction on long text."""
        text = "This is a very long text that should be truncated at word boundary"
        result = extract_text_snippet(text, max_length=20)
        assert result.endswith("...")
        assert len(result) < len(text)

    def test_extract_snippet_none(self):
        """Test snippet extraction on None."""
        result = extract_text_snippet(None)
        assert result is None


class TestDateParsing:
    """Tests for dates.py utilities."""

    def test_parse_relative_date_hace_dias(self):
        """Test parsing 'hace X días' format."""
        result = parse_relative_date("hace 3 días")
        assert result is not None
        # Should be approximately 3 days ago
        delta = datetime.utcnow() - result
        assert 2 < delta.days < 4

    def test_parse_relative_date_hace_horas(self):
        """Test parsing 'hace X horas' format."""
        result = parse_relative_date("hace 2 horas")
        assert result is not None
        delta = datetime.utcnow() - result
        # Should be approximately 2 hours ago
        assert 1 <= delta.total_seconds() / 3600 <= 3

    def test_parse_relative_date_english(self):
        """Test parsing English 'X days ago' format."""
        result = parse_relative_date("2 days ago")
        assert result is not None
        delta = datetime.utcnow() - result
        assert 1 < delta.days < 3

    def test_parse_relative_date_none(self):
        """Test parsing None returns None."""
        result = parse_relative_date(None)
        assert result is None

    def test_parse_relative_date_unparseable(self):
        """Test parsing unparseable date returns None."""
        result = parse_relative_date("2025-01-15")
        assert result is None

    def test_is_within_date_range_recent(self):
        """Test date range filter for recent."""
        now = datetime.utcnow()
        
        # 2 days ago - should be within 'recent' (3 days)
        recent = now - timedelta(days=2)
        assert is_within_date_range(recent, 'recent')
        
        # 5 days ago - should NOT be within 'recent'
        old = now - timedelta(days=5)
        assert not is_within_date_range(old, 'recent')

    def test_is_within_date_range_last_week(self):
        """Test date range filter for last week."""
        now = datetime.utcnow()
        
        # 5 days ago - within last week
        recent = now - timedelta(days=5)
        assert is_within_date_range(recent, 'last_week')
        
        # 10 days ago - not within last week
        old = now - timedelta(days=10)
        assert not is_within_date_range(old, 'last_week')

    def test_is_within_date_range_none_date(self):
        """Test date range filter with None date."""
        # None date should always pass
        assert is_within_date_range(None, 'recent')
        assert is_within_date_range(None, 'last_week')

    def test_is_within_date_range_none_filter(self):
        """Test date range filter with None filter."""
        now = datetime.utcnow()
        # None filter should always pass
        assert is_within_date_range(now, None)
