"""Example OSINT plugin – a template for plugin authors.

This plugin demonstrates the expected interface.  Replace the body of
``collect`` with real OSINT logic.  Always respect rate-limiting,
terms of service, and privacy laws.  Only use OSINT data for authorised
security testing.
"""

from __future__ import annotations

from typing import Any, Dict


def collect(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich *profile* with OSINT-derived data (example no-op)."""
    if profile.get("firstname"):
        keywords = profile.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]
        keywords.append("osint_enriched")
        profile["keywords"] = keywords
    return profile
