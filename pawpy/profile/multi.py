"""Multi-target profile handling with cross-referencing."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from rich.console import Console

console = Console()


def load_multi_profiles(path: str) -> List[Dict[str, Any]]:
    """Load a JSON array of profiles from *path*."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array of profiles in {path}, "
            f"but got {type(data).__name__}. "
            "Use -j / --import-json for a single profile."
        )
    return data


def merge_profiles(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple profiles into a single unified profile."""
    merged: Dict[str, Any] = {
        "firstname": [],
        "lastname": [],
        "nickname": [],
        "birthdate": [],
        "partner": [],
        "partner_nick": [],
        "partner_bdate": [],
        "pet": [],
        "company": [],
        "hometown": [],
        "favourite_color": [],
        "children": [],
        "keywords": [],
    }
    list_fields = {"children", "keywords"}

    for profile in profiles:
        for key in merged:
            value = profile.get(key, "")
            if key in list_fields:
                if isinstance(value, list):
                    merged[key].extend(v for v in value if v)
            elif key in ("birthdate", "partner_bdate"):
                if isinstance(value, str) and value.strip():
                    merged[key].append(value.strip())
            else:
                if isinstance(value, str) and value.strip():
                    merged[key].append(value.strip())

    for key in merged:
        seen = set()
        unique = []
        for item in merged[key]:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        merged[key] = unique

    console.print(
        f"[green]✓[/green] Merged {len(profiles)} profiles into unified cross-referenced profile."
    )
    return merged


def extract_merged_base_words(merged: Dict[str, Any]) -> List[str]:
    """Flatten all fields from a merged profile into a deduplicated word list."""
    words: set = set()
    for key, value in merged.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    words.add(item.strip().lower())
        elif isinstance(value, str) and value.strip():
            words.add(value.strip().lower())
    return sorted(words)


def extract_merged_dates(merged: Dict[str, Any]) -> List[str]:
    """Extract all date strings from a merged profile."""
    dates: set = set()
    for field in ("birthdate", "partner_bdate"):
        for d in merged.get(field, []):
            if isinstance(d, str) and d.strip():
                dates.add(d.strip())
    return sorted(dates)
