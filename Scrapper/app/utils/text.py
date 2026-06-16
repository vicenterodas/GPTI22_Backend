"""
Text processing utilities.
"""

import re


def clean_text(text: str | None) -> str | None:
    """
    Clean and normalize text content.
    
    - Removes extra whitespace (multiple spaces, tabs)
    - Normalizes line breaks
    - Strips leading/trailing whitespace
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text or None if input is None
    """
    if text is None:
        return None

    # Replace multiple spaces/tabs with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text if text else None


def extract_text_snippet(text: str | None, max_length: int = 200) -> str | None:
    """
    Extract a snippet from text, respecting word boundaries.
    
    Args:
        text: Text to extract from
        max_length: Maximum length of snippet (before truncation)
        
    Returns:
        Snippet of text or None
    """
    if not text:
        return None

    text = clean_text(text)
    if not text:
        return None

    if len(text) <= max_length:
        return text

    # Truncate and remove partial word at the end
    truncated = text[:max_length]
    # Find last space before max_length
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + "..." if truncated else None
