"""Date permutation engine.

Takes dates in DDMMYYYY format and produces many common sub-string
variants: day, month, year, two-digit year, reversed, and combinations.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse a DDMMYYYY string into a datetime.  Returns None on failure."""
    date_str = date_str.strip()
    if len(date_str) != 8 or not date_str.isdigit():
        return None
    try:
        return datetime.strptime(date_str, "%d%m%Y")
    except ValueError:
        return None


def date_permutations(date_str: str) -> List[str]:
    """Generate date-based password fragments from a DDMMYYYY date string.

    Produces: day, month, year (4-digit), year (2-digit), DDMM, MMDD,
    DDMMYY, MMDDYY, YYYYMMDD, DD/MM/YYYY, MM/DD/YYYY, YYYY,
    and reverse forms.
    """
    dt = _parse_date(date_str)
    if dt is None:
        return []

    d = f"{dt.day:02d}"
    m = f"{dt.month:02d}"
    y4 = str(dt.year)
    y2 = y4[-2:]

    parts = [
        d,
        m,
        y4,
        y2,
        f"{d}{m}",
        f"{m}{d}",
        f"{d}{m}{y2}",
        f"{m}{d}{y2}",
        f"{d}{m}{y4}",
        f"{m}{d}{y4}",
        f"{y4}{m}{d}",
        f"{y4}{d}{m}",
        f"{d}/{m}/{y4}",
        f"{m}/{d}/{y4}",
        f"{d}-{m}-{y4}",
        f"{m}-{d}-{y4}",
        f"{d}.{m}.{y4}",
        f"{m}.{d}.{y4}",
        y4,
        y2,
        f"{m}{d}",
        f"{d}{m}",
    ]

    # Deduplicate while preserving order
    seen = set()
    result = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result
