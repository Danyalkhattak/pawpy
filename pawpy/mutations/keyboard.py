"""Keyboard walk generator.

Produces password candidates from continuous keyboard walks on QWERTY
and other common layouts.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

# QWERTY keyboard adjacency map (row, col) -> set of (row, col) neighbours
_QWERTY_LAYOUT = [
    "`1234567890-=",
    " qwertyuiop[]\\",
    " asdfghjkl;'",
    "  zxcvbnm,./",
]

# Build adjacency: each key maps to its neighbours (up to 8 directions)
_QWERTY_POS: Dict[str, Tuple[int, int]] = {}
_QWERTY_ADJ: Dict[str, List[str]] = {}

for _r, row in enumerate(_QWERTY_LAYOUT):
    for _c, ch in enumerate(row):
        if ch == " ":
            continue
        _QWERTY_POS[ch] = (_r, _c)

for _key, (_kr, _kc) in _QWERTY_POS.items():
    neighbours = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = _kr + dr, _kc + dc
            for other_key, (or_, oc) in _QWERTY_POS.items():
                if or_ == nr and oc == nc:
                    neighbours.append(other_key)
    _QWERTY_ADJ[_key] = neighbours


# Classic static keyboard walks
STATIC_WALKS = [
    "qwerty",
    "qwert",
    "asdf",
    "asdfgh",
    "zxcvbn",
    "zxcv",
    "qazwsx",
    "1qaz2wsx",
    "qweasd",
    "!@#$%",
    "1234567890",
    "0987654321",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1q2w3e4r",
    "q1w2e3r4",
    "zaq1xsw2",
    "1234qwer",
    "poiuytrewq",
    "lkjhgfdsa",
    "mnbvcxz",
    "!qaz2wsx3edc",
    "1qaz!QAZ",
]


def static_keyboard_walks() -> List[str]:
    """Return the built-in list of classic keyboard walk patterns."""
    return list(STATIC_WALKS)


def dynamic_keyboard_walks(min_len: int = 4, max_len: int = 8) -> List[str]:
    """Generate all possible continuous keyboard walks up to *max_len*.

    Uses BFS from each starting key, following adjacency relationships
    on the QWERTY layout.  Only walks of length >= *min_len* are returned.

    Note: This can produce a very large number of candidates.  For
    max_len=8 the count is in the millions.  Use with caution.
    """
    results: Set[str] = set()

    for start_key in _QWERTY_POS:
        # BFS
        queue: List[Tuple[str, str]] = [(start_key, start_key)]
        while queue:
            current, walk = queue.pop(0)
            if len(walk) >= min_len:
                results.add(walk)
            if len(walk) >= max_len:
                continue
            for neighbour in _QWERTY_ADJ.get(current, []):
                queue.append((neighbour, walk + neighbour))

    return sorted(results)
