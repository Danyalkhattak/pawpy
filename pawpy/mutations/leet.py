"""Leet-speak mutation engine.

Supports multiple substitution tables and generates all possible
combinations of leet substitutions for a given word.
"""

from __future__ import annotations

import itertools
from typing import Dict, List, Set

# Comprehensive leet substitution maps
_LEET_MAPS: List[Dict[str, List[str]]] = [
    # Level 1: basic
    {"a": ["@"], "e": ["3"], "i": ["1"], "o": ["0"], "s": ["$"], "t": ["7"]},
    # Level 2: extended
    {"a": ["@"], "e": ["3"], "i": ["1", "!"], "o": ["0"], "s": ["$", "5"], "t": ["7"]},
    # Level 3: aggressive
    {
        "a": ["@", "4"],
        "e": ["3"],
        "i": ["1", "!"],
        "o": ["0"],
        "s": ["$", "5"],
        "t": ["7"],
        "l": ["1"],
        "b": ["8"],
        "g": ["9"],
        "h": ["#"],
    },
]


def leet_speak(word: str, level: int = 2) -> List[str]:
    """Generate leet-speak variations of *word*.

    For each character that has substitutions, generate all combinations
    of original vs. substituted forms.  Returns a list of unique variants
    (always includes the original word).

    Args:
        word: The base word to leetify.
        level: Substitution table to use (1=basic, 2=extended, 3=aggressive).

    Returns:
        List of unique leet-speak variants.
    """
    level = max(1, min(level, len(_LEET_MAPS)))
    table = _LEET_MAPS[level - 1]
    results: Set[str] = set()

    # Build a list of options per character position
    char_options: List[List[str]] = []
    for ch in word.lower():
        subs = table.get(ch, [])
        if subs:
            char_options.append([ch] + subs)
        else:
            char_options.append([ch])

    # Generate all combinations
    for combo in itertools.product(*char_options):
        results.add("".join(combo))

    return sorted(results)
