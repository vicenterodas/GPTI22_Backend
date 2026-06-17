"""
Date/time parsing and utilities.
"""

from datetime import datetime, timedelta
import re


def parse_relative_date(date_str: str | None) -> datetime | None:
    """
    Parse relative date strings like "hace 3 días", "hace 2 horas", etc.
    
    Args:
        date_str: String like "hace 2 días" or "2 days ago"
        
    Returns:
        Approximate datetime or None if unparseable
    """
    if not date_str:
        return None

    date_str = date_str.lower().strip()

    # Pattern: "hace X [días/horas/minutos/semanas]"
    match = re.search(r'hace\s+(\d+)\s+(día|hora|minuto|semana)s?', date_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)

        if unit == 'día':
            return datetime.utcnow() - timedelta(days=num)
        elif unit == 'hora':
            return datetime.utcnow() - timedelta(hours=num)
        elif unit == 'minuto':
            return datetime.utcnow() - timedelta(minutes=num)
        elif unit == 'semana':
            return datetime.utcnow() - timedelta(weeks=num)

    # Pattern: "X days ago"
    match = re.search(r'(\d+)\s+(day|hour|minute|week)s?\s+ago', date_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)

        if unit == 'day':
            return datetime.utcnow() - timedelta(days=num)
        elif unit == 'hour':
            return datetime.utcnow() - timedelta(hours=num)
        elif unit == 'minute':
            return datetime.utcnow() - timedelta(minutes=num)
        elif unit == 'week':
            return datetime.utcnow() - timedelta(weeks=num)

    return None


def parse_date_string(date_str: str | None) -> datetime | None:
    """
    Try parsing a date string that may be relative (handled by parse_relative_date)
    or absolute in several common formats, including ISO `YYYY-MM-DD HH:MM:SS`
    and Spanish textual dates like `11 de Junio de 2026 18:36:16`.

    Returns a timezone-naive UTC datetime or None if unparseable.
    """
    if not date_str:
        return None

    # First try relative formats
    rel = parse_relative_date(date_str)
    if rel:
        return rel

    s = date_str.strip()

    # Try ISO-like formats
    iso_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
    ]
    for fmt in iso_formats:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue

    # Try Spanish textual: e.g. '11 de Junio de 2026 18:36:16' or '11 de Junio de 2026'
    # Map spanish month names to numbers (lowercase)
    months = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'setiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    import re
    m = re.search(r"(\d{1,2})\s+de\s+([A-Za-zñÑ]+)\s+de\s+(\d{4})(?:\s+(\d{1,2}:\d{2}:\d{2}))?", s)
    if m:
        day = int(m.group(1))
        mon_name = m.group(2).lower()
        year = int(m.group(3))
        time_part = m.group(4)
        mon = months.get(mon_name)
        if mon:
            if time_part:
                try:
                    t = datetime.strptime(time_part, "%H:%M:%S").time()
                    return datetime(year, mon, day, t.hour, t.minute, t.second)
                except Exception:
                    return datetime(year, mon, day)
            else:
                return datetime(year, mon, day)

    return None


def is_within_date_range(
    published_date: datetime | None,
    date_range: str | None
) -> bool:
    """
    Check if a published date falls within a requested date range.
    
    Args:
        published_date: Date to check (may be None)
        date_range: Range filter: 'recent', 'last_week', 'last_month', None
        
    Returns:
        True if within range or if both are None, False otherwise
    """
    if published_date is None or date_range is None:
        return True

    now = datetime.utcnow()

    if date_range == 'recent':
        # Last 3 days
        return (now - timedelta(days=3)) <= published_date
    elif date_range == 'last_week':
        return (now - timedelta(weeks=1)) <= published_date
    elif date_range == 'last_month':
        return (now - timedelta(days=30)) <= published_date

    return True
