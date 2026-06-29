"""Hybrid attack mode – combine base words with mask patterns.

Simulates hashcat -a 6 (word + right mask) and -a 7 (left mask + word).
"""

from __future__ import annotations

import logging
import string
from itertools import product
from typing import List, Optional

logger = logging.getLogger("pawpy.generator.hybrid")

# Mask character mapping
_MASK_MAP = {
    "?l": string.ascii_lowercase,
    "?u": string.ascii_uppercase,
    "?d": string.digits,
    "?s": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~",
    "?a": string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;':\",./<>?`~",
}


def _parse_mask(mask: str) -> List[str]:
    """Parse a hashcat-style mask string into a list of character sets.

    Supports: ?l, ?u, ?d, ?s, ?a, and literal characters.
    """
    result = []
    i = 0
    while i < len(mask):
        if mask[i] == "?" and i + 1 < len(mask):
            token = mask[i : i + 2]
            if token in _MASK_MAP:
                result.append(_MASK_MAP[token])
                i += 2
                continue
        # Literal character
        result.append([mask[i]])
        i += 1
    return result


def _expand_mask(mask_parts: List[List[str]], max_results: int = 100_000) -> List[str]:
    """Expand a parsed mask into all possible combinations, with a safety cap."""
    # Calculate total combinations
    total = 1
    for part in mask_parts:
        total *= len(part)
        if total > max_results:
            logger.warning(
                "Mask produces %d combinations (capped to %d). "
                "Consider using a shorter mask.",
                total,
                max_results,
            )
            break

    results = []
    for combo in product(*mask_parts):
        results.append("".join(combo))
        if len(results) >= max_results:
            break
    return results


def hybrid_generate(
    words: List[str],
    left_mask: Optional[str] = None,
    right_mask: Optional[str] = None,
) -> List[str]:
    """Generate hybrid attack candidates.

    Args:
        words: Base word list.
        left_mask: Hashcat-style mask to prepend (simulates -a 7).
        right_mask: Hashcat-style mask to append (simulates -a 6).

    Returns:
        List of word+mask combinations.
    """
    results = []

    if right_mask:
        mask_parts = _parse_mask(right_mask)
        mask_vals = _expand_mask(mask_parts, max_results=1_000)
        for word in words:
            for mv in mask_vals:
                results.append(f"{word}{mv}")

    if left_mask:
        mask_parts = _parse_mask(left_mask)
        mask_vals = _expand_mask(mask_parts, max_results=1_000)
        for word in words:
            for mv in mask_vals:
                results.append(f"{mv}{word}")

    return results
